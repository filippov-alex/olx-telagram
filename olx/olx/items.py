# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OlxItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    currency = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()
    district = scrapy.Field()
    region = scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    images = scrapy.Field()
    created = scrapy.Field()
