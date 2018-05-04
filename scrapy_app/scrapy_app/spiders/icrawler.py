# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, Rule
from ..items import Product
import json
import logging



class IcrawlerSpider(SitemapSpider):
    name = 'icrawler'


    def __init__(self, *args, **kwargs):
        # We are going to pass these args from our django view.
        # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.sitemap_urls = [self.url]
        self.allowed_domains = [self.domain]
        self.attributesJson = kwargs.get('attributesJson')

        super(IcrawlerSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # You can tweak each crawled page here
        # Don't forget to return an object.
        att_dict = json.loads(self.attributesJson)
        elt = dict()
        for k, v in att_dict.items():
            elt[k] = response.xpath(v).extract()
            elt['url'] = response.url
        yield elt


