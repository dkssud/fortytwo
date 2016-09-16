import scrapy
from robot.items import NewsItem
from scrapy.contrib.loader import ItemLoader
import re
import string
from urlparse import urlparse


class NewsSpider(scrapy.Spider):

    # crawler setting
    name = "twt_web_backup"

    # allowed_domains = ["news.jtbc.joins.com"]

    f = open('/srv/tmp/twt/url.txt')
   
    #store urls and freqs into different columns
    start_urls = []
    dic_id = {}
    dic_freq = {}

    count = 0
    for line in f.readlines():
        columns = line.split("\t")
        line1 = columns[0]
        line2 = columns[1]
        line3 = columns[2]
        start_urls.append(line2)
        dic_id[line2] = line1
        dic_freq[line2] = line3.rstrip('\n')
        count += 1

    f.close()

    print start_urls
    print count

    
    #initilaize output file
    def __init__(self, category=None):

        self.url_out = open("/srv/tmp/twt/spider_url.txt", 'w')

    #parser
    def parse(self, response):

        #original URL extract
        url = []
        try:
            url = response.request.meta['redirect_urls']
            url_origin = url[0]
        except KeyError:
            url = response.request.url
            url_origin = url

        url_origin = url_origin.replace('?_escaped_fragment_=', '#!')
        print "url origin = " + url_origin

        line = ItemLoader(item=NewsItem(), response=response)

        # appear freq, original URL add
        line.add_value('sid', NewsSpider.dic_id[str(url_origin)])
        line.add_value('appear_freq', NewsSpider.dic_freq[str(url_origin)])
        line.add_value('target_url', str(url_origin))

        # domain add
        parsed_uri = urlparse(str(url_origin))
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        print domain
        line.add_value('domain', domain)

        print >> self.url_out, '%s\t%s\t%s' % (NewsSpider.dic_id[str(url_origin)], url_origin, NewsSpider.dic_freq[str(url_origin)])



        body_html = response.body
        body_html = re.sub(r'<(no|)script[^>]*>(.*?)</(no|)script>', '', body_html, flags = re.DOTALL)
        body_html = re.sub(r'<style[^>]*>(.*?)</style>', '', body_html, flags = re.DOTALL)
        body_html = re.sub(r'<!--(.*?)-->', '', body_html, flags = re.DOTALL)

        print body_html



        #classify into news and other
        p = re.compile('\wnews\.|news\.+|media\.|bizn\.')
        if_news = p.search(response.url)



        if 1 > 2 :

            #JTBC News, Daum News title
            line.add_xpath('title', '//div[re:match(@class, "[A-Za-z0-9_]subject|[A-Za-z0-9]title|tit_[A-Za-z0-9]|title")]//h3//text()')
            
            #KHAN title
            line.add_xpath('title', '//h3[re:match(@class, "tit_subject")]/text()')

            #Yonhapnews title
            line.add_xpath('title', '//div[re:match(@class, "article-wrap")]//h2/text()')

            #Daum News sub_title
            line.add_xpath('sub_title', '//h4/strong/text()')

            #KHAN desc
            line.add_xpath('body', '//span[re:match(@class, "article_txt")]/text()')  

            #JTBC News desc
            line.add_xpath('body', '//div[re:match(@class, "[A-Za-z0-9_]content")]/text()')

            #Daum News desc
            line.add_xpath('body', '//div[re:match(@class, "[A-Za-z0-9_]content")]/h4/text()')

            #Yonhapnews desc
            line.add_xpath('body', '//div[re:match(@class, "[A-Za-z0-9_]article|article")]/p/text()')  
            #line.add_xpath('link', '//a[contains(@href, "http://")]/@href')


            #JTBC News, Yonhapnews last_updated
            line.add_xpath('last_updated', '//span[re:match(@class, "i_date|pblsh")]/text()')
            
            #Daum News last_updated
            line.add_xpath('last_updated', '//meta[contains(@property, "article:published_time")]/@content')

            #Ohmynews last_updated
            line.add_xpath('last_updated', '//div[contains(@class, "info_data")]/div/text()')

            #KHAN last_updated
            line.add_xpath('last_updated', '//p[contains(@class, "time")]/text()')

        else:

            tag_regex_1 = '//meta[contains(@name, "keywords")]/@content'
            img_regex_1 = '//meta[re:match(@property, "og:image")]/@content'
            domain_regex_1 = '//meta[contains(@property, "og:site_name")]/@content'
            author_regex_1 = '//meta[contains(@name, "author")]/@content'
            author_regex_2 = '//meta[contains(@name, "Author")]/@content'
            short_url_regex_1 = '//meta[re:match(@name, "short_url")]/@content'

            date_regex_1 = '//meta[re:match(@name, "(?<!vali)date|.(?<!vali)date")]/@content'
            date_regex_2 = '//span[contains(@class, "published updated")]/text()'
            date_regex_3 = '//span[contains(@property, "date")]/@content'

            body_regex_1 = '//section[contains(@class, "article")]'
            body_regex_2 = '//section[contains(@id, "article")]'
            body_regex_3 = '//div[contains(@class, "article")]'
            body_regex_4 = '//div[contains(@class, "post-content")]'
            body_regex_5 = '//div[contains(@class, "content")]'
            body_regex_6 = '//div[contains(@class, "body")]'
            body_regex_7 = '//*[contains(@class, "description")]'
            body_regex_8 = '//article'
            body_regex_9 = '//div'


            # title
            line.add_xpath('title', '//title/text()')

            # body
            if response.xpath(body_regex_1):
                line.add_xpath('body', body_regex_1+'//p//text()')
                body_regex = body_regex_1
            elif response.xpath(body_regex_2):
                line.add_xpath('body', body_regex_2+'//p//text()')
                body_regex = body_regex_2
            elif response.xpath(body_regex_3):
                line.add_xpath('body', body_regex_3+'//p//text()')
                body_regex = body_regex_3
            elif response.xpath(body_regex_4):
                line.add_xpath('body', body_regex_4+'//p//text()')
                body_regex = body_regex_4
            elif response.xpath(body_regex_5):
                line.add_xpath('body', body_regex_5+'//text()')
                body_regex = body_regex_5
            elif response.xpath(body_regex_6):
                line.add_xpath('body', body_regex_6+'//text()')
                body_regex = body_regex_6
            elif response.xpath(body_regex_7):
                line.add_xpath('body', body_regex_7+'//text()')
                body_regex = body_regex_7
            elif response.xpath(body_regex_8):
                line.add_xpath('body', body_regex_8+'//text()')
                body_regex = body_regex_8
            else:
                line.add_xpath('body', body_regex_9+'/text()')
                body_regex = body_regex_9

            # sub_title
            line.add_xpath('sub_title', body_regex+'//h1//text()')
            line.add_xpath('sub_title', body_regex+'//h2//text()')
            line.add_xpath('sub_title', body_regex+'//h3//text()')
            line.add_xpath('sub_title', body_regex+'//h4//text()')
            line.add_xpath('sub_title', body_regex+'//h5//text()')
            line.add_xpath('sub_title', body_regex+'//h6//text()')
            line.add_xpath('sub_title', body_regex+'//b//text()')
            line.add_xpath('sub_title', body_regex+'//strong//text()')

            # tag
            line.add_xpath('tag', tag_regex_1)

            # image
            line.add_xpath('img', img_regex_1)

            # date
            if response.xpath(date_regex_1):
                line.add_xpath('date', date_regex_1)
            elif response.xpath(date_regex_2):
                line.add_xpath('date', date_regex_2)
            elif response.xpath(date_regex_3):
                line.add_xpath('date', date_regex_3)
            else:
                line.add_xpath('date', '//@datetime')


            # domain
            if response.xpath(domain_regex_1):
                line.replace_xpath('domain', domain_regex_1)

            # short url
            line.add_xpath('short_url', short_url_regex_1)

            # img more
            line.add_xpath('body_img', body_regex+'//img/@src')

            # link
            line.add_xpath('link_url', body_regex+'//p/a/@href')

            # author
            if response.xpath(author_regex_1):
                line.add_xpath('author', author_regex_1)
            else:
                line.add_xpath('author', author_regex_2)



            #Wordpress sub_title
            #line.add_xpath('sub_title', '//h6/text()')
            #line.add_xpath('sub_title', '//h5/text()')

            #Youtube desc
            #line.add_xpath('body', '//div[contains(@id, "watch-description-text")]/p/text()')

            #Wordpreass, Podbbang desc
            #line.add_xpath('body', '//div[re:match(@class, "su-note|desc_area")]//text()')
         
            #engadget desc
            #line.add_xpath('body', '//div[re:match(@class, "[A-Za-z0-9-]content")]/p/text()')



            #Mashable image_caption
            #line.add_xpath('image_caption', '//div[re:match(@class, "image-credit")]/text()')


            #Naver Blog last_updated
            #line.add_xpath('last_updated', '//em[contains(@class, "num")]/text()')

            #Wordpress last_updated
            #line.add_xpath('last_updated', '//span[re:match(@class, "date")]//text()')

            #engadget last_updated
            #line.add_xpath('last_updated', '//span/@datetime')

            #Mashable last_updated
            #line.add_xpath('last_updated', '//time/text()')

            #Youtube last_updated
            #line.add_xpath('last_updated', '//strong[contains(@class, "watch-time-text")]/text()')


        yield line.load_item()
