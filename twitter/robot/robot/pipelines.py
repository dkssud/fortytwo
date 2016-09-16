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
from scrapy.exceptions import DropItem


class JsonWriterPipeline(object):


    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.file = {}


    def spider_opened(self, spider):

        #file name : spider name
        self.file = codecs.open("/srv/_tmp/web.json", "w", encoding="utf-8")


    def process_item(self, item, spider):
        
        #json with indent
        #line = json.dumps(dict(item), ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
        
        #json without indent
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        
        self.file.write(line)
        return item
		

    def spider_closed(self, spider):
        self.file.close()
