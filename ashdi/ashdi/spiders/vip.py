import json
import re
import scrapy
import sys
from pathlib import Path
project_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_dir))
from database.items import UkinoItem
from database.db_creator import get_max_id
BASE_URL = "https://ashdi.club/{}/nkZR6o0l/"
TOTAL_TARGET = 25364


class AshdiSpider(scrapy.Spider):
    name = "ashdi"
    allowed_domains = ["ashdi.club"]
    begin = get_max_id("content") + 1

    def start_requests(self):
        for i in range(self.begin, TOTAL_TARGET + 1):
            yield scrapy.Request(
                url=BASE_URL.format(i),
                callback=self.parse,
                meta={"original_id": i}
            )

    def parse_title(self, title_raw):
        match = re.search(r'^(.*?)(?:\s/\s(.*?))?\s\((\d{4})\)$', title_raw)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return title_raw, None, None

    def parse(self, response):
        original_id = response.meta["original_id"]
        if response.body.decode() == "error":
            return
        tw_title = response.xpath('//meta[@name="twitter:title"]/@content').get()
        if not tw_title:
            tw_title = response.xpath('//div[@class="title"]/text()').get()
        tw_url = response.xpath('//iframe/@src').get()
        if not tw_url:
            tw_url = response.xpath('//meta[@name="twitter:url"]/@content').get()
        
        tw_img = response.xpath('//meta[@name="twitter:image"]/@content').get()

        if not tw_url:
            return # can have link to movie

        content_type = "serial" if "serial" in tw_url else "film"
        ukr, eng, year = self.parse_title(tw_title)
        j_data = json.dumps({
                "source": "ashdi.club",
                "club_link": response.url,
                "vip_link": tw_url
            })
        item = UkinoItem(
            _id=original_id,
            title_ua=ukr,
            title_or=eng,
            type_src=content_type,
            year=year,
            poster=tw_img,
            director=None,
            description=None,
            imdb=None,
            m3u_links=tw_url,
            json=j_data
        )

        yield item
