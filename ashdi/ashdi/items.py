# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FilmItem(scrapy.Item):
    type = scrapy.Field()
    title = scrapy.Field()
    ukr_name = scrapy.Field()
    eng_name = scrapy.Field()
    year = scrapy.Field()
    vip_link = scrapy.Field()
    image_link = scrapy.Field()
    club_link = scrapy.Field()
    original_id = scrapy.Field()