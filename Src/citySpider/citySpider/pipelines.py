# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Src.SQLHelper.MySQLHelper import MySqlHelper


class CityspiderPipeline(object):
    def open_spider(self, spider):
        print("start crawling")
        self.helper = MySqlHelper()
        self.helper.connect()

    def close_spider(self, spider):
        print("finish crawling")
        self.helper.close()

    def submit(self, item):
        sql = "INSERT INTO nationalCity(cityName, provinceName, longitude, latitude, scale) VALUES(%s, %s, %s, %s, %s)"
        self.helper.insert(sql, item["cityName"], item["provinceName"], item["longitude"], item['latitude'], item["scale"])

    def process_item(self, item, spider):
        if(item != None):
            self.submit(item)
        return
