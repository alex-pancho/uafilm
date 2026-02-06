# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UkinoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title_ua = scrapy.Field()
    title_or = scrapy.Field()
    type_src = scrapy.Field()
    year = scrapy.Field()
    director = scrapy.Field()
    description = scrapy.Field()
    poster = scrapy.Field()
    json = scrapy.Field()
    imdb = scrapy.Field()

