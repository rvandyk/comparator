# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, Rule
from ..items import Product



class IcrawlerSpider(SitemapSpider):
    name = 'icrawler'


    def __init__(self, *args, **kwargs):
        # We are going to pass these args from our django view.
        # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.sitemap_urls = [self.url]
        self.allowed_domains = [self.domain]

        super(IcrawlerSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # You can tweak each crawled page here
        # Don't forget to return an object.
        product = Product()
        product['title'] = response.xpath('//title/text()').extract()
        product['price'] = response.xpath(
            'descendant-or-self::strong[contains(@data-price, "priceET")]/text()').extract()
        product['url'] = response.url
        yield product