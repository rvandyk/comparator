# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import Product
import json
import logging



class IcrawlerSpider(CrawlSpider):
    name = 'icrawler'


    def __init__(self, *args, **kwargs):
        # We are going to pass these args from our django view.
        # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]
        self.attributesJson = kwargs.get('attributesJson')

        IcrawlerSpider.rules = [
            Rule(LinkExtractor(unique=True), callback='parse_item', follow=True),
        ]

        super(IcrawlerSpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        # You can tweak each crawled page here
        # Don't forget to return an object.

        att_dict = json.loads(self.attributesJson)
        elt = dict()
        for k, v in att_dict.items():
            elt[k] = response.xpath(v).extract()
            elt['url'] = response.url
        yield elt


