# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


#class RobotPipeline(object):
#    def process_item(self, item, spider):
#        return item

import json
import codecs
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class JsonWriterPipeline(object):

    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = {}

    def spider_opened(self, spider):
		self.file = codecs.open("/users/mala/hack/python/out/crawl_raw/%s.json" % spider.name, "wb", encoding="utf-8")

    def process_item(self, item, spider):
		line = json.dumps(dict(item), ensure_ascii=False) + "\n"
		self.file.write(line)
		return item
		
    def spider_closed(self, spider):
        self.file.close()
