# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class CityspiderItem(Item):
    cityName = Field()
    provinceName = Field()
    longitude = Field()
    latitude = Field()
    scale = Field()
