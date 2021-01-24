import scrapy
import json
from lxml import html as ET
from ukino.items import UkinoItem


class KinoSpider(scrapy.Spider):
    name = "nserv"

    def res_return(self, response):
        try:
            res = json.loads(response.text)
            return res
        except json.decoder.JSONDecodeError:
            self.failures += 1
            self.logger.error('JSON parse error retrying')
            return []

    def start_requests(self, url=None):
        urls = [
            'http://nserv.host:5300/eneyida/list?cat=films',
            'http://nserv.host:5300/uakino/list?cat=filmi',
            'http://nserv.host:5300/kinoukr/list?cat=films',
            # "http://nserv.host:5300/eneyida/list?cat=cartoon",
            # "http://nserv.host:5300/uakino/list?cat=cartoon",
            # "http://nserv.host:5300/kinoukr/list?cat=cartoon"
             ]
        if url is None:
            for url in urls:
                yield scrapy.Request(url=url, callback=self.pre_parse)
        else:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = self.res_return(response)
        ch = item.get("channels", [])

        def get_type():
            type_src = "Кіно"
            if response.url.find("cat=cartoon") != -1:
                type_src = "Мульт"
            elif response.url.find("cat=film") != -1:
                type_src = "Кіно"
            return type_src

        title_ua = None
        type_src = get_type()
        title_or = None
        poster = ""
        desc = ""
        year = ""
        director = ""
        all_links = {}

        if len(ch) > 0:
            for i in ch:
                if i.get("title") == "Описание":
                    desc = str(i.get("description", "[]"))
                    tree = ET.fromstring(desc)
                    names = tree.xpath('//*[@id="title"]//text()')[0].split(" / ")
                    #     names = tree.xpath('//*[@id="title"]//text()')
                    title_ua = names[0]
                    if len(names) > 1:
                        title_or = names[-1]
                    poster = tree.xpath('//img[@src]')[0].attrib["src"]
                    texts = tree.xpath('//div[3]/text()')
                    year = texts[0].split(",")[-1].strip()
                    director = texts[-1].strip()
                    desc_sh = tree.xpath('//*[@id="footer"]/text()')[0]
                    desc = desc_sh.strip()
                elif i.get("title") != "Описание" and i.get("title") != "Трейлер":
                    qa = i.get("title", "1080p")
                    if qa == "Воспроизвести":
                        qa = "1080p"
                    link = i.get("stream_url")
                    all_links.update({qa: link})

        item_dict = dict(
            title_ua=title_ua, type_src=type_src, title_or=title_or,
            poster=poster,
            desc=desc, year=year, director=director, all_links=all_links
             )
        if "Слишком много запросов ;(" not in item_dict.get('all_links'):
            itm = UkinoItem(**item_dict)
            yield itm
        else:
            print("У сервера лінька", item_dict.get('all_links'))

    def pre_parse(self, response):
        cont = self.res_return(response)
        if isinstance(cont, dict):
            items = cont.get("channels")
            for i in items[:-1]:
                item_url = i.get("playlist_url", "")
                yield scrapy.Request(url=item_url, callback=self.parse)
            old_url = response.url
            next_page_url = cont.get("next_page_url", old_url)
            if old_url != next_page_url:
                print(next_page_url)
                yield scrapy.Request(url=next_page_url, callback=self.pre_parse)
            else:
                pass
                # print(old_url, next_page_url)
        else:
            print("Look, its all!")
            return
