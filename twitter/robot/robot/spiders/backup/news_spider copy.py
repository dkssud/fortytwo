# -*- coding: utf-8 -*-

import scrapy
from robot.items import NewsItem
from scrapy.contrib.loader import ItemLoader
import re
import string
from urlparse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import hashlib
import datetime


class NewsSpider(scrapy.Spider):

    # crawler name
    name = "twt_web"

    # allowed_domains = ["news.jtbc.joins.com"]

    # url file open
    f = open('/srv/tmp/twt/url.txt')
   
    # store urls and freqs into different columns
    start_urls = []
    dic_url = {}
    dic_freq = {}
    dic_date = {}

    count = 0
    for line in f.readlines():
        columns = line.split("\t")
        line1 = columns[0]
        line2 = columns[1]
        line3 = columns[2]
        line4 = columns[3]
        start_urls.append(line2)
        dic_url[line1] = line2
        dic_date[line1] = line3
        dic_freq[line1] = line4.rstrip('\n')
        count += 1

    f.close()

    # log start_urls & their count
    print start_urls
    print count

    
    # initilaize output file
    def __init__(self, category=None):

        self.url_out = open("/srv/tmp/twt/spider_url.txt", 'w')


    # parser
    def parse(self, response):


        # pre-process

        # original URL extract to find target_url
        url = []
        try:
            url = response.request.meta['redirect_urls']
            url_origin = url[0]
        except KeyError:
            url_origin = response.request.url

        # exception handing for '?_escapeed_fragment_' case
        url_origin = url_origin.replace('?_escaped_fragment_=', '#!')

        uid = hashlib.sha1(str(url_origin)).hexdigest()

        # itemloader
        line = ItemLoader(item=NewsItem(), response=response)

        # id, appear freq, original URL, refer date add
        line.add_value('sid', uid)
        line.add_value('appear_freq', NewsSpider.dic_freq[uid])
        line.add_value('target_url', str(url_origin))
        line.add_value('date', NewsSpider.dic_date[uid])

        # extract domain and add
        parsed_uri = urlparse(str(url_origin))
        domain_url = '{uri.netloc}'.format(uri=parsed_uri)
        line.add_value('domain', domain_url)



        # article - pre-process

        # remove unnecessory parts of html : script, style, annotation
        html = response.body
        html = re.sub(r'<(no|)script\b[^>]*>(.*?)</(no|)script>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style\b[^>]*>(.*?)</style>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<iframe\b[^>]*>(.*?)</iframe>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<!--(.*?)-->', '', html, flags = re.DOTALL)

        # store html into soup format
        try:
            body_soup = BeautifulSoup(html, from_encoding="utf-8")
        except HTMLParseError, e:
            raise e
 

        # meta

        # title
        try:
            title = body_soup.find('title')
            title = str(title)
            title = re.sub(r'<(/?)title>', '', title, flags = re.IGNORECASE)
            print title
            line.add_value('title', title)
        except (TypeError, KeyError), e:
            pass 

        # domain
        try:
            domain = body_soup.find('meta', attrs={'property' : re.compile(r"og:site_name", re.I)})
            domain = str(domain['content'])
            line.replace_value('domain', domain)
        except (TypeError, KeyError), e:
            pass

        # rep_img
        try:
            img = body_soup.find('meta', attrs={'property' : re.compile(r"og:image", re.I)})
            rep_img = str(img['content'])
            rep_img = re.sub(r' (.*)', '', rep_img)
            line.add_value('img', rep_img)
        except (TypeError, KeyError), e:
            pass

        # author
        try:
            author = body_soup.find('meta', attrs={'name' : re.compile(r"(.*?)author(.*?)", re.I)})
            author = str(author['content'])
            line.add_value('author', author)
        except (TypeError, KeyError), e:
            pass

        # tag, keyword
        try:
            for keyword in body_soup.find_all('meta', attrs={'name' : re.compile(r"(.*?)(tag|keyword)(.*?)", re.I)}):
                keyword = str(keyword['content'])
                line.add_value('tag', keyword)
        except (TypeError, KeyError), e:
            pass

        # short urls
        try:
            short_url = body_soup.find('meta', attrs={'name' : re.compile(r"short.url(|s)", re.I)})
            short_url = short_url['content']
            line.add_value('short_url', short_url)
        except (TypeError, KeyError), e:
            pass

        # language
        try:
            lang = body_soup.find('html')
            lang = str(lang['lang'])
            line.add_value('lang', lang)
        except (TypeError, KeyError), e:
            pass


        # date

        # rule to extract date
        date_name_regex = r"(.*?)(?<!vali)date(.*)"
        date_regex_1 = r"(19|20)([0-9][0-9])(\.|\/|-| |)(0[1-9]|1[012])(\.|\/|-| |)(0[1-9]|[12][0-9]|3[01])"
        date_regex_2 = r"(19|20)([0-9][0-9])(\.|\/|-| )(0[1-9]|1[012])(\.|\/|-| )(0[1-9]|[12][0-9]|3[01])"
        date_regex_3 = r"(19|20)([0-9][0-9])(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])"
        date_regex_4 = r"^[0-9]+$"
        date_regex_5 = r"(19|20)([0-9][0-9])-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])"

        # date extract from meta
        date_rule = '999'
        date = ''
        date_matched = ''
        #try:
        if body_soup.find('meta', attrs={'name' : re.compile(date_name_regex, re.I)}):
            tag = body_soup.find('meta', attrs={'name' : re.compile(date_name_regex, re.I)})
            date_rule = '//meta/@name'
            date = tag['content']
        #except (TypeError,AttributeError), e:
        #    pass
        if body_soup.find('meta', attrs={'property': re.compile(date_name_regex, re.I)}):
            tag = body_soup.find('meta', attrs={'property': re.compile(date_name_regex, re.I)})
            date_rule = '//meta@property'
            date = tag['content']

        # date extract from body
        if date_rule == '999':
            try:
                found = body_soup.find(content=re.compile(date_regex_1))
                date = found['content']
                date_rule = '//body/@content'
            except (TypeError,AttributeError), e:
                pass
        if date_rule == '999':
            try:
                found = body_soup.find(text=re.compile(date_regex_1))
                date = found.string
                date_rule = '//body/@text'
            except (TypeError,AttributeError), e:
                pass

        # standardize date format
        try:
            m = re.search(date_regex_2, date)
            date_matched = str(m.group(0))
            date_matched = re.sub(r"(\.|/| )", "-", date_matched)
        except:
            pass
        try:
            m = re.search(date_regex_4, date)
            date = str(m.group(0))
            date_matched = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
        except:
            pass
        try:
            m = re.search(date_regex_3, date)
            date_matched = str(m.group(1)) + str(m.group(2)) + '-' + str(m.group(3)) + '-' + str(m.group(4))
        except:
            pass

        print date_rule
        print date
        print date_matched


        # store date into flat
        try:
            if re.match(date_regex_5, date_matched):
                line.replace_value('date', str(date_matched)+' 00:00:00')
        except TypeError, e:
            pass

        line.add_value('date_rule', str(date_rule))




        # body #1 : by tag regex

        # remove unnecesoory parts of html again : head, foot
        html = re.sub(r'<head(|er)\b[^>]*>(.*?)</head(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<foot(|er)\b[^>]*>(.*?)</foot(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)

        # store html into soup format again
        try:
            body_soup = BeautifulSoup(html, from_encoding="utf-8")
        except HTMLParseError, e:
            raise e

        # initialize body_rule and body_html
        body_rule = '999'
        body_html = ''

        # regex to extract body
        body_regex = r'(.*?)(article|content|body|description)(.*?)'

        if body_soup.find('section', attrs={'id': re.compile(body_regex, re.I)}):
            tag = body_soup.find('section', attrs={'id': re.compile(body_regex, re.I)})
            body_rule = '//section/@id'
        if body_rule == '999':
            tag = body_soup.find('section', attrs={'class': re.compile(body_regex, re.I)})
            body_rule = '//section/@class'
        if body_rule == '999':
            tag = body_soup.find('div', attrs={'class': re.compile(body_regex, re.I)})
            body_rule = '//div@class'
        if body_rule == '999':    
            tag = body_soup.find('article')
            body_rule = '//article'
        if body_rule != '999':
            body_html = str(tag.contents)
        
        #print body_html

        # body #2 : by complicated '\n' method

        if body_rule == '999':

            # remove unlikely tags
            unlikely_rule = r"today|title|review|byline|dropdown|sns|relation|click|hotissue|reply|subscribe|auth|hotnews|skip|gnb|sidebar|banner|ad-|ad_|-ad|_ad|next|previous|tools|follow|nav|share|sharing|suggestions|link|related|combx|comment|community|disqus|extra|foot|footer|header|menu|remark|rss|shoutbox|sponsor|agegate|pagination|pager|popup|cookie|channel"
            likely_rule = re.compile(r"body|article|content|description|desc|with", flags = re.IGNORECASE)
            for tag in body_soup.find_all(attrs={'class': re.compile(unlikely_rule, re.I)}):
                print 'unlikely_matched'
                print str(tag['class'])
                if likely_rule.search(str(tag['class'])):
                    print '-> likely_matched'
                elif tag.name == 'section':
                    print '-> section'
                else: 
                    tag.extract()
            for tag in body_soup.find_all(attrs={'id': re.compile(unlikely_rule, re.I)}):
                print 'unlikely_matched'
                print str(tag['id'])
                if likely_rule.search(str(tag['id'])):
                    print '-> likely_matched'
                elif tag.name == 'section':
                    print '-> section'
                else: 
                    tag.extract()
            body_html = str(body_soup)

        #print body_html

        # declare array and variables
        body_arr = []
        body_arr_100 = []
        body_arr_50 = []
        body_arr_25 = []
        body_arr_0 = []
        body_html_from_arr = ''
        
        # remove h/b/strong/em/i/p tags and convert tags into '\n'
        body_html_to_arr = re.sub(r'<(/?)(h[0-9]|b|strong|em|i|p|br|a|small|q|span)>', ' ', body_html, flags = re.DOTALL)        
        body_html_to_arr = re.sub(r'<(/?[^>]+?)>', '\n', body_html_to_arr, flags = re.DOTALL)

        #print body_html_to_arr

        # make body_arr
        body_arr = body_html_to_arr.split('\n\n\n')

        # pack and uniq body_arr
        for b in body_arr:
            b = re.sub(r'(\n|\r|\t)', ' ', b)
            b = re.sub(r'\s\s+', ' ', b)
            b = re.sub(r'(&#[0-9]+;)|(^\s)|(\s$)', '', b)
            if b == '' or b == ' ':
                pass
            elif len(b) > 100:
                if b not in body_arr_100:
                    #print "---" + '\n' + b + '\n' + str(len(b)) + '\n'
                    body_arr_100.append(b)
            elif len(b) > 50:
                if b not in body_arr_50:
                    body_arr_50.append(b)
            elif len(b) > 25:
                if b not in body_arr_25:
                    body_arr_25.append(b)
            else:
                if b not in body_arr_0:
                    body_arr_0.append(b)

        if len(body_arr_100) > 0:
            body_html_from_arr = " ".join(body_arr_100)
            body_rule += ' divide by tag counts and length 100'
        elif len(body_arr_50) > 0:
            if body_rule == '999':
                body_html_from_arr = " ".join(body_arr_50)
                body_rule = ' divide by tag counts and length 50'

        if body_rule is not '999':
            body_html = body_html_from_arr

        print body_rule
        #print body_html

        # length check
        body_len = len(body_html)
        print body_len


        #body_html = str(body_html).encode('utf-8')
        
        # body
        line.add_value('body', body_html)
        line.add_value('body_rule', str(body_rule))

        # img urls and link urls

        # store html into soup format again
        #try:
        #    body_soup = BeautifulSoup(body_html)
        #except HTMLParseError, e:
        #    raise e

        # extract image urls in body
        #for img in body_soup.find_all('img'):
        #    try:
        #        line.add_value('body_img', img['src'])
        #    except KeyError, e:
        #        pass

        # extract link urls in body
        #for url in body_soup.find_all('a'):
        #    try:
        #        url = url['href']
        #        if url == '#':
        #            pass
        #        elif re.match(r'^(http|https)://', url):
        #            line.add_value('link_url', url)
        #        elif re.match(r'^//', url):
        #            line.add_value('link_url', 'http:' + url)
        #        else:
        #            line.add_value('link_url', 'http://' + domain_url + url)
        #    except KeyError, e:
        #        pass






        if body_len > 25 and len(title) > 0:
            # store id, url, freq into log file for crawl error check
            print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid])
            yield line.load_item()
        else:
            pass
