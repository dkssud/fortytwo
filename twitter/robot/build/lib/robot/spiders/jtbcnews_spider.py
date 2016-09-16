import scrapy
from robot.items import JtbcNewsItem


class JtbcNewsSpider(scrapy.Spider):
    name = "jtbcnews"
    allowed_domains = ["joins.com"]
    start_urls = [
        "http://news.jtbc.joins.com/html/194/NB10617194.html"
    ]

    def parse(self, response):

        for sel in response.xpath('//body'):
            item = JtbcNewsItem()
            item['title'] = sel.xpath('//div[contains(@class, "title")]/h3/text()').extract()
            item['desc'] = sel.xpath('//div[contains(@class, "article_content")]/text()').extract()
            item['link'] = sel.xpath('//a[contains(@href, "http://")]/@href').extract()
            item['last_updated'] = sel.xpath('//span[contains(@class, "i_date")]/text()').extract()


            yield item
