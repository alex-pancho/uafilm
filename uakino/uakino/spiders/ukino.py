import scrapy
from scrapy import Selector
from .core import CoreSpider
from ..items import UkinoItem


class BaseURL:
    base_url = 'https://uakino.club/'  # https://uakino.club/index.php?do=cat&category=filmi&box_mac=112233
    mac = dict(box_mac='11223344')


class UkinoSpider(CoreSpider, BaseURL):
    name = 'ukino'
    start_urls = [BaseURL.base_url]

    def start_requests(self, url=None):
        """
        Get the first page of the section
        :param url: URL for parsing
        """
        pages = ['seriesss']  # , 'cartoon', 'filmi'
        if url is None:
            for page in pages:
                kwords = dict(do="cat", category=page, **self.mac)
                yield scrapy.FormRequest(url=self.base_url, method='GET', formdata=kwords, callback=self.pre_parse)
        else:
            yield scrapy.FormRequest(url=url, method='GET', formdata=self.mac, callback=self.parse)

    def pre_parse(self, response):
        """
        Get information about all the movies and series from the current page of the section, move on.
        :param response: scrapy response
        """
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
        selector = Selector(response=response, type="xml").xpath('//channel').getall()
        for ch in selector:
            if ch.find('<channel>', 2) != -1:
                ch = ch[:ch.find('<channel>', 2)]
            ch = Selector(text=ch, type="xml")
            item_url = ch.xpath("./playlist_url/text()").get()
            description = ch.xpath('//center/text()').get()
            item = dict(title_ua=ch.xpath("./title/text()").get(),
                        title_or="",
                        imdb="",
                        json={},
                        description=description,
                        year=ch.xpath("//b/a/text()").get(),
                        shot=ch.xpath("./logo_30x30/text()").get(),
                        type_src=type_src)
            if type_src == 'series':
                season = self.tag_cleaner(ch.xpath("//b[contains(text(), 'сезон')]").get())
                item["series"] = {"season": season}
            yield scrapy.FormRequest(url=item_url, method='GET', formdata=self.mac, callback=self.parse, cb_kwargs=item)
        for next_page in scrapy.Selector(response=response, type="xml").xpath('//next_page_url'):
            next_page_url = next_page.xpath("./text()").get()
            yield scrapy.FormRequest(url=next_page_url, method='GET', formdata=self.mac, callback=self.pre_parse)

    def parse(self, response, **item):
        """
        Find links to all series or all versions of the film in different qualities
        :param response: scrapy response
        :param item: current movie or series dict
        """
        select = Selector(response=response, type="xml").xpath('//channel').getall()
        for ch in select:
            ch = Selector(text=ch, type="xml")
            title = ch.xpath("./title/text()").get()
            if item['type_src'] != 'series':
                stream_url = ch.xpath("./stream_url/text()").get()
                description = ch.xpath("./description/text()").get()
            else:
                stream_url = {}
                names = ch.xpath("//title/text()").getall()[1:]
                for name in names:
                    name_url = ch.xpath(f'//*[contains(text(), "{name}")]/../stream_url/text()').get()
                    stream_url[name] = name_url
                description = Selector(response=response, type="xml").xpath('//all_description/text()').get()
            if "https://www.youtube.com/" in stream_url:
                continue
            description = self.tag_cleaner(description)
            categories = self.get_text_key(description, "Категорія:")
            director = self.get_text_key(description, "Режисер:")
            year = self.get_text_key(description, "Рік:")
            actors = self.get_text_key(description, "Актори:")
            item.update({"categories": categories, "actors": actors, "director": director})
            if year != item.get("year"):
                item["year"] = year
            if item['type_src'] != 'series':
                yield scrapy.Request(url=stream_url, method='GET', callback=self.post_parse, cb_kwargs=item)
            else:
                if len(item['description']) < len(description):
                    start = description.find(actors) + len(actors)
                    item['description'] = description[start:]
                    if "title" not in item['series']:
                        item['series'].update({"title": []})
                    item['series']["title"].append(title)
                for name, stream in stream_url.items():
                    item['series']["title"].append(name)
                    yield scrapy.Request(url=stream, method='GET', callback=self.post_parse, cb_kwargs=item)

    def post_parse(self, response, **item):
        """
        Get link to m3u streaming file
        :param response: scrapy response
        :param item: current movie or series dict
        """
        body = response.text
        kwords = "var player = new Playerjs"
        start = body.find(kwords) + len(kwords)+2
        end = body.find("});", start)
        src = body[start:end].replace("\n", "").replace("\t", "")
        video_data = [s.split(":") for s in src.split(",")[:-1]]
        i = {"json": {}}
        vd = []
        for v in video_data:
            if v[0] == "id":
                vd.append(dict(id=v[1:]))
            elif v[0] != "":
                if v[0] == 'file':
                    v[0] = "m3u_link"
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
        yield UkinoItem(**i)
