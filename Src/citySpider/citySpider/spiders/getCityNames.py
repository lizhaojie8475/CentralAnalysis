# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from Src.citySpider.citySpider.items import CityspiderItem


class GetcitynamesSpider(scrapy.Spider):
    name = 'getCityNames'
    start_urls = ['http://data.acmr.com.cn/member/city/city_md.asp']

    def start_requests(self):
        return [Request(url=self.start_urls[0])]

    def parse(self, response):
        selectors = response.selector.xpath('//tr/td/table[@class="maintext"]')
        selectors = selectors[3:8]
        for selector in selectors:
            scale = selector.xpath('.//font/a/text()').extract()
            names = selector.xpath('.//td/text()').extract()
            names = map(lambda name: re.sub(r"\s+", "", name), names)
            names = filter(lambda name: name != "", names)
            names = list(names)
            for name in names:
                full_name = name.split("省")
                if len(full_name) == 1:
                    provinceName = full_name[0]
                    cityName = full_name[0]
                else:
                    provinceName = full_name[0] + "省"
                    cityName = full_name[1]

                item = CityspiderItem()
                item["cityName"] = cityName
                item["provinceName"] = provinceName
                item["longitude"] = ""
                item["latitude"] = ""
                item["scale"] = scale
                yield item


