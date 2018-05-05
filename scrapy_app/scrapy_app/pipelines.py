# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from mainapp.models import ScrapyItem, CrawlerModel
import json
import logging

class ScrapyAppPipeline(object):
    def __init__(self, crawler_id, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        self.items = []
        self.crawler = CrawlerModel.objects.get(id=crawler_id)

    @classmethod
    def from_crawler(cls, crawler):
        logging.log(logging.WARNING, crawler.settings.get('crawler_id'))
        return cls(
            unique_id=crawler.settings.get('unique_id'), # this will be passed from django view
            crawler_id=crawler.settings.get('crawler_id')
        )

    def close_spider(self, spider):
        # And here we are saving our crawled data with django models.
        item = ScrapyItem()
        item.unique_id = self.unique_id
        item.data = self.items
        item.crawler = self.crawler
        item.save()
        self.crawler.running = False
        self.crawler.save()


    def process_item(self, item, spider):
        if item['price']:
            self.items.append(json.dumps(dict(item)))
        return item
