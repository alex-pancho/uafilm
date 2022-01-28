import scrapy
from .core import CoreSpider
from ..items import UkinoItem

class BaseURL:
    base_url = 'https://uakino.club/'  # https://uakino.club/index.php?do=cat&category=filmi&box_mac=112233
    mac = dict(box_mac='11223344')
    all_desc = []


class UkinoSpider(CoreSpider, BaseURL):
    name = 'ukino'
    start_urls = [BaseURL.base_url]

    def start_requests(self, url=None):
        pages = ['seriesss', 'cartoon', 'filmi']
        if url is None:
            for page in pages:
                self.category = page
                kward = dict(do="cat", category=page, **self.mac)
                yield scrapy.FormRequest(url=self.base_url, method='GET', formdata=kward, callback=self.pre_parse)
        else:
            yield scrapy.FormRequest(url=url, method='GET', formdata=self.mac, callback=self.parse)

    def pre_parse(self, response):
        type_src = ""
        if 'filmi' in response.url:
            type_src = 'movie'
        elif 'cartoon' in response.url:
            type_src = 'cartoon'
        elif 'seriesss' in response.url:
            type_src = 'series'
        # items = UkinoItem()
        #   # and then inside for:
        # items['title_ua'] = ch.xpath("./title/text()").get()
        for ch in scrapy.Selector(response=response, type="xml").xpath('//channel'):
            item_url = ch.xpath("./playlist_url/text()").get()
            description = ch.xpath('//center').getall()
            if len(self.all_desc) >= 40:
                self.all_desc = []
            desc = self.tag_cleaner(description[len(self.all_desc)])
            if desc not in self.all_desc:
                self.all_desc.append(desc)

            item = dict(title_ua=ch.xpath("./title/text()").get(),
                       title_or="",
                       imdb="",
                       json={},
                       description=desc,
                       year=ch.xpath("//b/a/text()").get(),
                       shot=ch.xpath("./logo_30x30/text()").get(),
                       type_src=type_src)
            #item = dict(item=its)
            yield scrapy.FormRequest(url=item_url, method='GET', formdata=self.mac, callback=self.parse, cb_kwargs=item)
        for next_page in scrapy.Selector(response=response, type="xml").xpath('//next_page_url'):
            next_page_url = next_page.xpath("./text()").get()
            yield scrapy.FormRequest(url=next_page_url, method='GET', formdata=self.mac, callback=self.pre_parse)

    def parse(self, response, **item):
        for ch in scrapy.Selector(response=response, type="xml").xpath('//channel'):
            title = ch.xpath("./title/text()").get()
            stream_url = ch.xpath("./stream_url/text()").get()
            if "https://www.youtube.com/" in stream_url:
                continue
            description = ch.xpath("./description/text()").get()
            description = self.tag_cleaner(description)
            categories = self.get_text_key(description, "Категорія:")
            director = self.get_text_key(description, "Режисер:")
            year = self.get_text_key(description, "Рік:")
            actors = self.get_text_key(description, "Актори:")
            item.update({"categories": categories, "actors": actors, "director": director})
            if year != item.get("year"): item["year"] = year
            #item = dict(item=item)
            yield scrapy.Request(url=stream_url, method='GET', callback=self.post_parse, cb_kwargs=item)

    def post_parse(self, response, **item):
        body = response.text
        cwords = "var player = new Playerjs"
        start = body.find(cwords) + len(cwords)+2
        end = body.find("});", start)
        src = body[start:end].replace("\n", "").replace("\t", "")
        video_data = [s.split(":") for s in src.split(",")[:-1]]
        i = {"json": {}}
        vd = []
        for v in video_data:
            if v[0] == "id":
                vd.append(dict(id=v[1:]))
            elif v[0] != "":
                if v[0] == 'file': v[0] = "m3u_link"
                val = ":".join(v[1:]).strip('"')
                if "[Українські]" in val:
                    val = {"ua": val.split("]")[-1]}
                vio = {v[0]: val}
                vd[-1].update(vio)
        item["m3u_links"] = vd
        for key in item:
            if key in UkinoItem.fields:
                i[key] = item[key]
            else:
                i["json"].update({key: item[key]})
        # print(i)
        yield UkinoItem(**i)
