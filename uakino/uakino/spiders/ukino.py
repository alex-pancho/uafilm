from scrapy import Selector
from scrapy import FormRequest
from scrapy import Request
from database.items import UkinoItem

from .core import CoreSpider
from ..settings import DEBUG
from urllib.parse import urlparse

class BaseURL:
    base_url = 'https://uakino.best/index.php'  # https://uakino.club/index.php?category=filmi&box_mac=112233
    mac = dict(box_mac='11223344')


class UkinoSpider(CoreSpider, BaseURL):
    name = 'ukino'
    start_urls = [BaseURL.base_url]

    def start_requests(self, url=None):
        """
        Get the first page of the section
        :param url: URL for parsing
        """
        pages = ['filmi', 'cartoon', 'seriesss']  #
        if url is None:
            for page in pages:
                kwords = dict(category=page, **self.mac)
                yield FormRequest(url=self.base_url, method='GET', formdata=kwords, callback=self.pre_parse)
        else:
            yield FormRequest(url=url, method='GET', formdata=self.mac, callback=self.parse)

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
                        type_src=type_src,
                        series={}
                        )
            if type_src == 'series':
                season = self.tag_cleaner(ch.xpath("//b[contains(text(), 'сезон')]").get())
                item["series"] = {"season": season}
            yield FormRequest(url=item_url, method='GET', formdata=self.mac, callback=self.parse, cb_kwargs=item)
        for next_page in Selector(response=response, type="xml").xpath('//next_page_url'):
            next_page_url = next_page.xpath("./text()").get()
            if DEBUG: continue
            yield FormRequest(url=next_page_url, method='GET', formdata=self.mac, callback=self.pre_parse)

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
                if "https://www.youtube.com/" in stream_url:
                    continue
                if item.get('description') is None:
                    item['description'] = ""
                description = ch.xpath("./description/text()").get()
                dict_update = self.get_detailed_values(description)
                year = dict_update.pop("year")
                if year != item.get("year"):
                    item["year"] = year
                item.update(**dict_update)
                yield Request(url=stream_url, method='GET', callback=self.post_parse, cb_kwargs=item)
            else:
                stream_url = {}
                sub_series = ch.xpath("//submenu").getall()
                for sub in sub_series:
                    sub = Selector(text=sub, type="xml")
                    name = sub.xpath('//title/text()').get()
                    stream = sub.xpath('//stream_url/text()').get()
                    if "https" not in stream:
                        self.logger.warning(f"Wrong url: {stream} for {name} in {item['title_ua']}")
                        stream = stream.replace('//ttps:', '')
                        s = urlparse(stream)
                        stream = f"https://{s.hostname}{s.path}"
                    if "uploadvideo.info" in stream:
                        # now its url does not work
                        self.logger.warning(f"URL {stream} unavailable and temporary disabled")
                        continue
                    stream_url[name] = stream
                description = Selector(response=response, type="xml").xpath('//all_description/text()').get()
                dict_update = self.get_detailed_values(description)
                year = dict_update.pop("year")
                if year != item.get("year"):
                    item["year"] = year
                item.update(**dict_update)
                desc = description.strip().splitlines()[-1]
                if desc is not None and item.get('description', '') is not None:
                    if len(item.get('description', '')) < len(desc):
                        item['description'] = desc
                for name, stream in stream_url.items():
                    item['series'].update(title=title)
                    item["name"] = name
                    yield Request(url=stream, method='GET', callback=self.post_parse, cb_kwargs=item)

    def post_parse(self, response, **item):
        """
        Get link to m3u streaming file
        :param response: scrapy response
        :param item: current movie or series dict
        """
        body = response.text
        kwords = "var player = new Playerjs"
        src = self.get_text_key(body, kwords, "});")
        if src is None:
            # wrong body, stop item processing
            if "may be for sale" in body:
                body = "Domain for sale"
            elif "not found" in body:
                body = "Source not found"
            self.logger.warning(f"wrong body, stop item processing:\t{body}")
            return None
        src = src.replace("'", '"').replace("\n", "\t").replace("\t", "").replace('({', '')

        _id = self.get_text_key(src, 'id:"', '"')
        file = self.get_text_key(src, 'file:"', '"')
        get_poster = self.get_text_key(src, 'poster:"', '"')
        sub = self.get_text_key(src, 'subtitle:"', '"')
        subtitle = sub if sub is not None else ""
        item["m3u_links"] = dict(id=_id, m3u_link=file, subtitle=subtitle)
        poster = item.get("shot", "") if get_poster is None else get_poster
        item["poster"] = poster
        if "[Українські]" in item["m3u_links"].get("subtitle", ""):
            item["m3u_links"]["subtitle"] = {"ua": subtitle.split("]")[-1]}
        i = {"json": {}}
        for key in item:
            if key in UkinoItem.fields:
                i[key] = item[key]
            else:
                i["json"].update({key: item[key]})
        yield UkinoItem(**i)
