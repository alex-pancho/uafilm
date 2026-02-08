import json
# import re
import scrapy
import sys
from scrapy import (
    FormRequest,
    Request,
    Selector
)
import sys
from pathlib import Path
project_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_dir))
from database.items import UkinoItem


class BaseURL:
    base_url = "https://uakino.best/index.php"
    mac = {"box_mac": "11223344"}


class UkinoSpider(scrapy.Spider, BaseURL):
    """
    Spider for parsing uakino.best XML playlists inside:
    <div id="dle-content"> <channel> ... </channel> </div>
    """
    name = "uakino"

    # -------------------------------
    # START REQUESTS
    # -------------------------------
    def start_requests(self):
        """
        Entry point. Request movie, cartoon and series categories.
        """
        pages = ["filmi", "cartoon", "seriesss"]

        for page in pages:
            params = dict(category=page, **self.mac)
            yield FormRequest(
                url=self.base_url,
                formdata=params,
                method="GET",
                callback=self.parse_list,
                cb_kwargs={"type_src": page},
            )

    # -------------------------------
    # PARSE LIST PAGE (many channels)
    # -------------------------------
    def parse_list(self, response, type_src):
        """
        Parse page with multiple <channel> blocks inside #dle-content
        """
        selector = Selector(response=response, type="xml").xpath('//*[@id="dle-content"]//channel').getall()
        for ch in selector:
            ch = Selector(text=ch, type="xml")
            item_url = ch.xpath("./playlist_url/text()").get()
            description = ch.xpath('//center/text()').get()
            title_ua = ch.xpath("./title/text()").get()
            year = ch.xpath("//b/a/text()").get()
            shot = ch.xpath("./logo_30x30/text()").get()
            playlist_url = item_url
            j_data = json.dumps({
                "source": "uakino.be",
                "club_link": response.url,
                "item_url": item_url
            })
            item = {
                "title_ua": title_ua,
                "title_or": "",
                "year": year,
                "poster": shot,
                "description": description,
                "type_src": self.normalize_type(type_src),
                "series": {},
                "json": j_data,
                "imdb": "",
            }

            # if item["type_src"] == "series":
            #     season = self.extract_season(description_raw)
            #     item["series"] = {"season": season}

            yield FormRequest(
                url=playlist_url,
                formdata=self.mac,
                method="GET",
                callback=self.parse_playlist,
                cb_kwargs={"item": item},
            )

        # pagination
        next_page = Selector(response=response, type="xml").xpath('//next_page_url/text()').get()
        if next_page:
            yield FormRequest(
                url=next_page,
                formdata=self.mac,
                method="GET",
                callback=self.parse_list,
                cb_kwargs={"type_src": type_src},
            )

    # -------------------------------
    # PARSE PLAYLIST PAGE
    # -------------------------------
    def parse_playlist(self, response, item):
        """
        Parse playlist page and extract stream URLs
        """
        channels = response.xpath("//channel")

        for ch in channels:
            stream_url = ch.xpath("./stream_url/text()").get()
            if not stream_url:
                continue

            if "youtube.com" in stream_url:
                continue

            yield Request(
                url=stream_url,
                callback=self.parse_stream,
                cb_kwargs={"item": dict(item)},  # copy!
            )

    # -------------------------------
    # PARSE PLAYER PAGE
    # -------------------------------
    def parse_stream(self, response, item):
        """
        Extract m3u8 from JS player
        """
        body = response.text

        src = self.extract_player_block(body)
        if not src:
            self.logger.warning(f"Player not found: {response.url}")
            return

        file = self.get_text_key(src, 'file:"', '"')
        poster = self.get_text_key(src, 'poster:"', '"')
        subtitle = self.get_text_key(src, 'subtitle:"', '"')

        item["m3u_links"] = {
            "m3u_link": file,
            "subtitle": subtitle or "",
        }

        if poster:
            item["poster"] = poster

        yield self.build_item(item)

    # -------------------------------
    # HELPERS
    # -------------------------------
    def normalize_type(self, raw):
        if raw == "filmi":
            return "movie"
        if raw == "cartoon":
            return "cartoon"
        if raw == "seriesss":
            return "series"
        return raw

    def extract_year(self, text):
        import re
        if not text:
            return None
        m = re.search(r"\b(19|20)\d{2}\b", text)
        return m.group(0) if m else None

    def extract_season(self, text):
        import re
        if not text:
            return None
        m = re.search(r"(\d+)\s*сезон", text)
        return m.group(1) if m else None

    def extract_player_block(self, body):
        key = "var player = new Playerjs"
        return self.get_text_key(body, key, "});")

    def build_item(self, data: dict):
        """
        Split fields into UkinoItem fields and json blob
        """
        out = {"json": {}}
        for k, v in data.items():
            if k in UkinoItem.fields:
                out[k] = v
            else:
                out["json"][k] = v
        return UkinoItem(**out)
