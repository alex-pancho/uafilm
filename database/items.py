# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from pathlib import Path
import sys
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))
from models import UkinoModel

class UkinoItem(scrapy.Item):
    _id = scrapy.Field()
    title_ua = scrapy.Field()
    title_or = scrapy.Field()
    type_src = scrapy.Field()
    year = scrapy.Field()
    director = scrapy.Field()
    description = scrapy.Field()
    poster = scrapy.Field()
    imdb = scrapy.Field()
    m3u_links = scrapy.Field()
    json = scrapy.Field()

    @classmethod
    def from_model(cls, model: UkinoModel):
        return cls(**model.__dict__)

