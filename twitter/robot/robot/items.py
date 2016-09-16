# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader.processor import Join, MapCompose, TakeFirst, Identity
from w3lib.html import remove_tags, replace_escape_chars, remove_entities

class WebItem(scrapy.Item):

    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    body = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    text = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    text_display = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    date = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    date_timestamp = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    freq = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    domain = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    domain_url = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    user_name = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    target_urls = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Identity(),
    )
    img_urls = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Identity(),
    )
    original_img_urls = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Identity(),
    )
    body_rule = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    date_rule = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    crawled_date = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    web_id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join(),
    )
    twt_ids = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Identity(),
    )
    tag = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_entities, replace_escape_chars),
        output_processor=Join(),
    )
    lang = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_entities, replace_escape_chars),
        output_processor=Join(),
    )





