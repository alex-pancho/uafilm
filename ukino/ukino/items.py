# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UkinoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title_ua=scrapy.Field()
    type_src=scrapy.Field()
    title_or=scrapy.Field() 
    poster=scrapy.Field() 
    desc=scrapy.Field()
    year=scrapy.Field()
    director=scrapy.Field()
    all_links=scrapy.Field()
    
