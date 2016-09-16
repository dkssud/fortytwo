# -*- coding: utf-8 -*-

#import json
#import urllib

import scrapy
from robot.items import WebItem
from scrapy.contrib.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.crawler import Crawler
#from scrapy.log import ScrapyFileLogObserver
import logging

from urlparse import urlparse
#from lxml import etree
from bs4 import BeautifulSoup

import re
import string
import hashlib
import datetime
import time

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def convertoUnixtime(inputdate):

    inputdate = re.sub(r'[\-:]', ' ', inputdate)
    inputdate = inputdate.split(' ')

    year = inputdate[0]
    month = inputdate[1]
    day = inputdate[2]
    hour = inputdate[3]
    minute = inputdate[4]
    second = inputdate[5]

    dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    ut = time.mktime(dt.timetuple())
    ut = int(ut)

    return ut


# news spider
class WebSpider(scrapy.Spider):

    # crawler name
    name = "web_spider"

    # allowed_domains = ["news.jtbc.joins.com"]

    # url file open
    f = open('/srv/_tmp/url.tmp')
   
    # store urls and freqs into different columns
    start_urls = []
    twt_ids = []
    dic_web_id = {}
    dic_url = {}
    dic_date = {}
    dic_date_timestamp = {}    
    dic_freq = {}
    dic_twt_ids = {}


    count = 0
    for line in f.readlines():
        line = line.rstrip('\n')
        columns = line.split("\t")
        web_id = columns[0]
        url = columns[1]
        date = columns[2]
        date_timestamp = columns[3]
        freq = columns[4]
        twt_ids = columns[5]
        if url not in start_urls:
            start_urls.append(url)
        dic_url[web_id] = url
        dic_date[web_id] = date
        dic_date_timestamp[web_id] = date_timestamp
        dic_freq[web_id] = freq
        dic_twt_ids[web_id] = twt_ids

        count += 1

    f.close()

    # log start_urls & their count
    print start_urls
    print count

    
    # initilaize output file
    def __init__(self, category=None):

        self.url_out = open("/srv/_tmp/spider_url.txt", 'w')
        self.url_filtered = open("/srv/_log/crawl_filtered.log", 'a')
        self.error = open("/srv/_log/crawl_error.log", 'a')

        #ScrapyFileLogObserver(open("/srv/twitter/tmp/spider.log", 'w'), level=logging.INFO).start()
        #PythonLoggingObserver(self.error, level=logging.ERROR).start()
        dispatcher.connect(self.spider_closed, signals.spider_closed)


    def spider_closed(self, spider, reason):

        self.log = open("/srv/_log/crawl.log", 'a')
        self.stats = self.crawler.stats
        print >> self.log, self.stats.get_value('response_received_count'), "crawled"
        print >> self.log, self.stats.get_value('item_scraped_count'), "scraped"
        print >> self.log, self.stats.get_value('log_count/ERROR'), "errors"
        #print >> self.log, "started at", self.stats.get_value('start_time')
        #print >> self.log, "finished at", self.stats.get_value('finish_time')


    # parser
    def parse(self, response):

        # pre-process

        # original URL extract to find target_url
        request_url_list = []
        url_origin_list = []
        try:
            request_url_list = response.request.meta['redirect_urls']
            url_origin = request_url_list[0]
        except KeyError:
            url_origin = response.request.url

        # exception handing for '?_escapeed_fragment_' case
        url_origin = url_origin.replace('?_escaped_fragment_=', '#!')
        uid = hashlib.sha1(str(url_origin)).hexdigest()
        url_origin_list.append(str(url_origin))

        # itemloader
        line = ItemLoader(item=WebItem(), response=response)

        # id, appear freq, original URL, refer date add
        #line.add_value('sid', uid)

        twt_ids_list = []
        line.add_value('target_urls', url_origin_list)
        line.add_value('web_id', uid)
        line.add_value('freq', WebSpider.dic_freq[uid])
        twt_ids = WebSpider.dic_twt_ids[uid]
        #print twt_ids
        twt_ids = twt_ids.lstrip('[')
        twt_ids = twt_ids.rstrip(']')
        twt_ids = twt_ids.replace('\'', '')
        twt_ids = twt_ids.replace(' ', '')
        twt_ids_list = twt_ids.split(',')
        #print twt_ids_list

        line.add_value('twt_ids', twt_ids_list)

        # extract domain and add
        domain_url = ''
        domain_name = ''
        parsed_uri = urlparse(str(url_origin))
        domain_url = '{uri.netloc}'.format(uri=parsed_uri)
        domain = domain_url
        date_final = WebSpider.dic_date[uid]


        # article - pre-process
        encoding = None
        if response.encoding == 'cp949':
            encoding = 'cp949'
            try:
                html = response.body_as_unicode()
                #print html
                html = str(html).decode('utf-8')
                #print html
            except:
                html = ''
        else:
            try:
                html = response.body
            except:
                html = ''

        #print html
        
        # remove unnecessory parts of html : script, style, annotation
        html = re.sub(r"<(no|)script\b[^>]*>(.*?)</(no|)script>", "", html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style\b[^>]*>(.*?)</style>", "", html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<iframe\b[^>]*>(.*?)</iframe>", "", html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<!--(.*?)-->", "", html, flags = re.DOTALL)

        #print html

        # store html into soup format
        try:
            body_soup = BeautifulSoup(html, from_encoding="utf-8")
        except HTMLParseError, e:
            print "soup error"
            raise e

        # meta

        # title
        title = None
        title_final = None

        try:
            title = body_soup.find('title')
            title = str(title.encode('utf-8'))
            title = re.sub(r'<(/?)title\b([^>]*?)>', '', title, flags = re.IGNORECASE)
            if title != '' and title != None:
                title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"title", re.I)}):
                title = body_soup.find('meta', attrs={'property' : re.compile(r"title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'name' : re.compile(r"title", re.I)}):
                title = body_soup.find('meta', attrs={'name' : re.compile(r"title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"twitter:title", re.I)}):
                title = body_soup.find('meta', attrs={'property' : re.compile(r"twitter:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'name' : re.compile(r"twitter:title", re.I)}):
                title = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"og:title", re.I)}):
                title = body_soup.find('meta', attrs={'property' : re.compile(r"og:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'name' : re.compile(r"og:title", re.I)}):
                title = body_soup.find('meta', attrs={'name' : re.compile(r"og:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title != '' and title != None:
                    title_final = title
        except:
            pass

        print "title : ", title_final


        # domain
        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"og:site_name", re.I)}):
                domain_name = body_soup.find('meta', attrs={'property' : re.compile(r"og:site_name", re.I)})
                domain_name = str(domain_name['content'].encode('utf-8'))
                if domain_name != '' and domain_name != None:
                    domain = domain_name
        except:
            pass


        # img
        img_list = []
        original_img_list = []
        
        try:
            img = body_soup.find('meta', attrs={'property' : re.compile(r"og:image", re.I)})
            img_og = str(img['content'].encode('utf-8'))
            img_og = re.sub(r' (.*)', '', img_og)
            if img_og != None and img_og != "null" and img_og != "none" and img_og !="":
                img_list.append(str(img_og))
                original_img_list.append(str(img_og))
        except:
            #print 'no facebook image'
            pass
        try:
            img = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:image", re.I)})
            img_tw = str(img['content'].encode('utf-8'))
            img_tw = re.sub(r' (.*)', '', img_tw)
            if img_tw != None and img_tw != "null" and img_tw != "none" and img_tw != "":
                original_img_list.append(str(img_tw))
        except:
            #print 'no twitter image'
            pass

        # add img_list
        try:
            if img_list != []:
                line.add_value('img_urls', img_list)
            if original_img_list != []:
                line.add_value('original_img_urls', original_img_list)
        except:
            #print 'no image'
            pass

        # desciption
        desc = None
        try:
            desc = body_soup.find('meta', attrs={'property' : re.compile(r"og:description", re.I)})
            desc = str(desc['content'].encode('utf-8'))
        except:
            pass

        if desc == '' or desc == None:
            try:
                desc = body_soup.find('meta', attrs={'name' : re.compile(r"og:description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass

        if desc == '' or desc == None:
            try:
                desc = body_soup.find('meta', attrs={'property' : re.compile(r"twitter:description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass

        if desc == '' or desc == None:
            try:
                desc = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass

        if desc == '' or desc == None:
            try:
                desc = body_soup.find('meta', attrs={'property' : re.compile(r"description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass

        if desc == '' or desc == None:
            try:
                desc = body_soup.find('meta', attrs={'name' : re.compile(r"description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass

        # author
        try:
            author = body_soup.find('meta', attrs={'name' : re.compile(r"(.*?)author(.*?)", re.I)})
            author = str(author['content'].encode('utf-8'))
            line.add_value('author', author)
        except:
            pass

        # tag, keyword
        try:
            for keyword in body_soup.find_all('meta', attrs={'name' : re.compile(r"(.*?)(tag|keyword)(.*?)", re.I)}):
                keyword = str(keyword['content'].encode('utf-8'))
                line.add_value('tag', keyword)
        except:
            pass

        # short urls
        #try:
        #    short_url = body_soup.find('meta', attrs={'name' : re.compile(r"short.url(|s)", re.I)})
        #    short_url = str(short_url['content'].encode('utf-8'))
        #    line.add_value('short_url', short_url)
        #except:
        #    pass

        # language
        try:
            lang = body_soup.find('html')
            lang = str(lang['lang'].encode('utf-8'))
            line.add_value('lang', lang)
        except:
            pass
            

        # robots
        robots = None
        try:
            robots = body_soup.find('meta', attrs={'name' : re.compile(r"robots", re.I)})
            robots = str(robots['content'].encode('utf-8'))
        except:
            pass


        # date

        # rule to extract date
        date_name_regex = r"(.*?)((?<!vali)(?<!current)(?<!expire_))date(.*)"
        date_regex_1 = r"(19|20)([0-9][0-9])(\.|\/|-| |)(0[1-9]|1[012])(\.|\/|-| |)(0[1-9]|[12][0-9]|3[01])"
        date_regex_2 = r"(19|20)([0-9][0-9])(\.|\/|-| )(0[1-9]|1[012])(\.|\/|-| )(0[1-9]|[12][0-9]|3[01])"
        date_regex_3 = r"(19|20)([0-9][0-9])(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])"
        date_regex_4 = r"^[0-9]+$"
        date_regex_5 = r"(19|20)([0-9][0-9])-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])"

        # date rule setting
        date_rule = '999'
        date = ''
        date_matched = ''

        # date extract from meta
        if body_soup.find('meta', attrs={'name' : re.compile(date_name_regex, re.I)}):
            tag = body_soup.find('meta', attrs={'name' : re.compile(date_name_regex, re.I)})
            date_rule = '//meta/@name'
            date = tag['content'].encode('utf-8')

        elif body_soup.find('meta', attrs={'property': re.compile(date_name_regex, re.I)}):
            tag = body_soup.find('meta', attrs={'property': re.compile(date_name_regex, re.I)})
            date_rule = '//meta@property'
            date = tag['content'].encode('utf-8')

        # date extract from body
        elif body_soup.find(datetime=re.compile(date_regex_1)):
            found = body_soup.find(datetime=re.compile(date_regex_1))
            date_rule = '//body/@datetime'
            date = found['datetime'].encode('utf-8')

        #elif body_soup.find(content=re.compile(date_regex_1)):
        #    found = body_soup.find(content=re.compile(date_regex_1))
        #    date_rule = '//body/@content'
        #    date = found['content'].encode('utf-8')

        #elif body_soup.find(text=re.compile(date_regex_1)):
        #   found = body_soup.find(text=re.compile(date_regex_1))
        #    date_rule = '//body/@text'
        #    date = found.string.encode('utf-8')

        # standardize date format
        if re.search(date_regex_2, date):
            m = re.search(date_regex_2, date)
            date_matched = str(m.group(0))
            date_matched = re.sub(r"(\.|/| )", "-", date_matched)

        elif re.search(date_regex_3, date):
            m = re.search(date_regex_3, date)
            date_matched = str(m.group(1)) + str(m.group(2)) + '-' + str(m.group(3)) + '-' + str(m.group(4))

        elif re.search(date_regex_4, date):
            m = re.search(date_regex_4, date)
            date = str(m.group(0))
            date_matched = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')

        # log
        #print 'date rule : ' + str(date_rule)
        #print date
        #print date_matched


        # store date into flat
        if re.match(date_regex_5, date_matched):
            date_final = str(date_matched)+' 00:00:00'

        # store datetime including unix time
        date_timestamp = convertoUnixtime(date_final)
        line.add_value('date', date_final)
        line.add_value('date_timestamp', str(date_timestamp))
        line.add_value('date_rule', str(date_rule))



        # body #1 : by tag regex

        # remove unnecesoory parts of html again : head, foot
        html = re.sub(r'<head(|er)\b[^>]*>(.*?)</head(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<foot(|er)\b[^>]*>(.*?)</foot(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)


        # store html into soup format
        try:
            body_soup = BeautifulSoup(html, from_encoding="utf-8")
        except HTMLParseError, e:
            print "soup error"
            raise e

        # initialize body_rule and body_html
        body_rule = '999'
        body_html = ''
        #print body_soup

        # regex to extract body
        #body_regex = r'article|content|body|description'
        #body_regex_minus = r'widget'

        #if body_soup.find('section', attrs={'id': re.compile(body_regex, re.I)}):
        #    tag = body_soup.find('section', attrs={'id': re.compile(body_regex, re.I)})
        #    body_rule = '//section/@id'
        #    body_html = str(tag.contents)
        #elif body_soup.find('section', attrs={'class': re.compile(body_regex, re.I)}):
        #    tag = body_soup.find('section', attrs={'class': re.compile(body_regex, re.I)})
        #    body_rule = '//section/@class'
        #    body_html = str(tag.contents)
        #elif body_soup.find('div', attrs={'id': re.compile(body_regex, re.I)}):
        #    tag = body_soup.find('div', attrs={'id': re.compile(body_regex, re.I)})
        #    body_rule = '//div@class'
        #    body_html = str(tag.contents)
        #elif body_soup.find('div', attrs={'class': re.compile(body_regex, re.I)}):
        #    tag = body_soup.find('div', attrs={'class': re.compile(body_regex, re.I)})
        #    body_rule = '//div@class'
        #    body_html = str(tag.contents)
        #if body_soup.find('article'):   
        #    tag = body_soup.find('article')
        #    body_rule = '//article'
        #    body_html = str(tag.contents)

        # remove unlikely tags
        bad_rule = r"review|aside|byline|dropdown|related|relation|rel|hotissue|reply|subscribe|auth|tabhot|hotnews|skip|banner|suggestions|comment|foot|footer|shoutbox|sponsor|rss|popup|cookie"
        unlikely_rule = r"today|sidebar|warning|title|carousel|widget|notice|popular|sns|click|gnb|banner|dncopy3|ad-|ad_|-ad|_ad|next|previous|tools|follow|nav|share|sharing|link|combx|community|disqus|extra|head|header|menu|remark|aggregate|pagination|channel"
        likely_rule = re.compile(r"read|body|article|content|wrap|description|desc|with|news|blog|post|pos|video|story", flags = re.IGNORECASE)

        for tag in body_soup.find_all(attrs={'class': re.compile(bad_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                #print 'bad matched'
                #print str(tag['class'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'class': re.compile(unlikely_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                #print 'unlikely_matched'
                #print str(tag['class'])
                if likely_rule.search(str(tag['class'])):
                    #print '-> likely_matched'
                    pass
                else: 
                    tag.extract()
        for tag in body_soup.find_all(attrs={'id': re.compile(bad_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:            
                #print 'bad matched'
                #print str(tag['id'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'id': re.compile(unlikely_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                #print 'unlikely_matched'
                #print str(tag['id'])
                if likely_rule.search(str(tag['id'])):
                    #print '-> likely_matched'
                    pass
                else: 
                    tag.extract()

        for tag in body_soup.find_all(attrs={'name': re.compile(bad_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:            
                #print 'bad matched'
                #print str(tag['name'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'name': re.compile(unlikely_rule, re.I)}):
            #print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                #print 'unlikely_matched'
                #print str(tag['name'])
                if likely_rule.search(str(tag['name'])):
                    #print '-> likely_matched'
                    pass
                else: 
                    tag.extract()

        body_html = str(body_soup)

        # log
        #print body_html


        # body post-process by complicated '\n' method

        # declare array and variables
        body_arr = []
        body_arr_140 = []
        body_html_from_arr_sum = ''
        body_html_from_arr_max = ''
        
        # remove h/b/strong/em/i/p tags and convert tags into '\n'
        body_html_to_arr = re.sub(r'<(/?)(h[0-9]|b|strong|em|i|p|br|a|small|q|span|img|blockquote)>', ' ', body_html, flags = re.DOTALL)        
        body_html_to_arr = re.sub(r'<(/?[^>]+?)>', '\n', body_html_to_arr, flags = re.DOTALL)

        #print body_html_to_arr

        # make body_arr
        body_arr = body_html_to_arr.split('\n\n\n\n\n')

        # pack and uniq body_arr
        for b in body_arr:
            b = re.sub(r'(\n|\r|\t)', ' ', b)
            b = re.sub(r'(\s\s+)', ' ', b)
            b = re.sub(r'(&#[0-9]+;)|(^\s)|(\s$)', '', b)
            #print b
            if b == '' or b == ' ':
                pass
            elif len(b) >= 140:
                if b not in body_arr_140:
                    #print b
                    body_arr_140.append(b)


        if len(body_arr_140) > 0:
            body_html_from_arr_max = max(body_arr_140, key=len)
            body_html_from_arr_sum = " ".join(body_arr_140)
            body_rule += ' length 140'


        if body_rule == '999':
            body_html = desc
        else:
            body_html = body_html_from_arr_max


        # length check
        #print 'body rule : ' + str(body_rule)
        body_len = len(str(body_html))
        #print "body length = " + str(body_len)
        title_len = len(str(title_final))


        # domain, crawled_date
        line.add_value('domain', str(domain))
        line.add_value('domain_url', str(domain_url))
        crawled_date = time.strftime('%Y-%m-%d %H:%M:%S')
        line.add_value('crawled_date', crawled_date)


        # set regex to process SNS docs
        domain_regex = re.compile(r"facebook|instagram|twitter|ask\.fm", flags = re.IGNORECASE)
        title_regex = re.compile(r"((.*?)facebook)|((.*?)instagram)|((.*?)twitter)|((.*?)ask\.fm)", flags = re.IGNORECASE)

        # check robots.txt and filter docs without title
        if robots == 'noindex':
            print >> self.url_filtered, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid], 'banned by robots.txt')
        #elif encoding == 'cp949':
        #    print >> self.url_filtered, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid], 'cp949')
        elif title_final == None or title_final == '':
            print >> self.url_filtered, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid], 'no title')

        # yield crawled docs
        elif body_html != None and body_html != '':
            # SNS
            if domain_regex.search(str(domain_url)):
                line.add_value('text', body_html)
                line.add_value('text_display', body_html)
                if title_regex.match(title_final):
                    title_match = title_regex.match(title_final)
                    domain = title_match.group()
                    line.replace_value('domain', domain)
                else:
                    line.replace_value('domain', title_final)
                yield line.load_item()
                print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid])

            # general
            else:
                line.add_value('title', title_final)
                line.add_value('body', body_html)
                line.add_value('body_rule', str(body_rule))
                yield line.load_item()
                print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid])

        elif img_list != []:

            # SNS
            if domain_regex.search(str(domain_url)):
                line.add_value('text', body_html)
                line.add_value('text_display', body_html)
                if title_regex.match(title_final):
                    title_match = title_regex.match(title_final)
                    domain = title_match.group()
                    line.replace_value('domain', domain)
                else:
                    line.replace_value('domain', title_final)
                yield line.load_item()
                print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid])

            # general
            else:
                line.add_value('title', title_final)
                line.add_value('body', body_html)
                line.add_value('body_rule', str(body_rule))
                yield line.load_item()
                print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid])

        else:
            print >> self.url_filtered, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, WebSpider.dic_date[uid], WebSpider.dic_freq[uid], 'no body & no image')






