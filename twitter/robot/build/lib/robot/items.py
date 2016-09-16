# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JtbcNewsItem(scrapy.Item):
	title = scrapy.Field()
	desc = scrapy.Field()
	link = scrapy.Field()
	last_updated = scrapy.Field(serializer=str)


	pass
    
    # define the fields for your item here like:
    # name = scrapy.Field()



