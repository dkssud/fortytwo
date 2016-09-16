# -*- coding: utf-8 -*-

import scrapy
from robot.items import WebItem
from scrapy.contrib.loader import ItemLoader
import re
import string
from urlparse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import hashlib
import datetime
import urllib
import ImageFile
import pycurl
import json
from StringIO import StringIO
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# function to get image size
def imgSizes(url):
    postData = '[\"' + str(url) + '\"]'
    #postData = postData.replace('\'',"\"")
    print postData
    result = StringIO()
    dic_result = {}

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://maddie.musian.net/tjcl/api/_img_cache/')
    c.setopt(pycurl.HTTPHEADER, ['Content-Type : application/x-www-form-urlencoded'])
    c.setopt(pycurl.POSTFIELDS, postData)
    c.setopt(pycurl.CUSTOMREQUEST, 'POST')
    c.setopt(c.WRITEFUNCTION, result.write)
    c.perform()

    result = result.getvalue()
    dic_result = json.loads(result)

    return dic_result

# news spider
class WebSpider(scrapy.Spider):

    # crawler name
    name = "web_spider"

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
        self.url_error = open("/srv/tmp/twt/spider_error.txt", 'w')


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
        line = ItemLoader(item=WebItem(), response=response)

        # id, appear freq, original URL, refer date add
        #line.add_value('sid', uid)
        line.add_value('appear_freq', WebSpider.dic_freq[uid])
        line.add_value('target_url', str(url_origin))
        line.add_value('date', WebSpider.dic_date[uid])

        # extract domain and add
        parsed_uri = urlparse(str(url_origin))
        domain_url = '{uri.netloc}'.format(uri=parsed_uri)
        line.add_value('domain', str(domain_url))


        # article - pre-process

        if response.encoding == 'cp949':
            html = ''
        else:
            html = response.body

        print html
        
        # remove unnecessory parts of html : script, style, annotation
        html = re.sub(r'<(no|)script\b[^>]*>(.*?)</(no|)script>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style\b[^>]*>(.*?)</style>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<iframe\b[^>]*>(.*?)</iframe>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<!--(.*?)-->', '', html, flags = re.DOTALL)

        # store html into soup format
        try:
            body_soup = BeautifulSoup(html, from_encoding="utf-8")
        except HTMLParseError, e:
            print "soup error"
            raise e

        #print body_soup

        # meta

        # title
        title = ''

        try:
            title = body_soup.find('title')
            title = str(title.encode('utf-8'))
            title = re.sub(r'<(/?)title\b([^>]*?)>', '', title, flags = re.IGNORECASE)
            if title is not '':
                line.add_value('title', title)
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'name' : re.compile(r"title", re.I)}):
                title = body_soup.find('meta', attrs={'name' : re.compile(r"title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title is not '':
                    line.replace_value('title', title)
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'name' : re.compile(r"twitter:title", re.I)}):
                title = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title is not '':
                    line.replace_value('title', title)
        except:
            pass

        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"og:title", re.I)}):
                title = body_soup.find('meta', attrs={'property' : re.compile(r"og:title", re.I)})
                title = str(title['content'].encode('utf-8'))
                if title is not '':
                    line.replace_value('title', title)
        except:
            pass

        print title


        # domain
        try:
            if body_soup.find('meta', attrs={'property' : re.compile(r"og:site_name", re.I)}):
                domain = body_soup.find('meta', attrs={'property' : re.compile(r"og:site_name", re.I)})
                domain = str(domain['content'].encode('utf-8'))
                if domain is not '':
                    line.replace_value('domain', domain)
        except:
            pass


        # img
        size_dic = {}
        img_list = []
        rep_img_size = 0
        
        try:
            img = body_soup.find('meta', attrs={'property' : re.compile(r"og:image", re.I)})
            img_og = str(img['content'].encode('utf-8'))
            img_og = re.sub(r' (.*)', '', img_og)
            img_list.append(str(img_og))
        except:
            print 'no facebook image'
            pass
        try:
            img = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:image", re.I)})
            img_tw = str(img['content'].encode('utf-8'))
            img_tw = re.sub(r' (.*)', '', img_tw)
            img_list.append(str(img_tw))
        except:
            print 'no twitter image'
            pass

        #print img_list
        try:
            for img_url in img_list:
                size = 0
                cached_url = ''
                size_dic = imgSizes(img_url)
                print size_dic
                size_dic = size_dic[str(img_url)]
                try:
                    size_dic = size_dic['conv']
                    cached_url = size_dic['url']
                    size_dic = size_dic['cachedFilesize']
                    size = size_dic['width']
                    print cached_url, size
                except:
                    pass
                if size > rep_img_size:
                    rep_img_size = size
                    rep_img_url = img_url
                    rep_img_cached_url = cached_url
            line.add_value('img', rep_img_url)
            line.add_value('cached_img', rep_img_cached_url)
        except:
            print 'image size error'
            pass


        #if size_og['width'] == 0 and size_tw['width'] == 0:
        #    pass
        #elif size_og['width'] >= size_tw['width']:
        #    line.add_value('img', img_og.encode('utf-8'))
        #else:
        #    line.add_value('img', img_tw.encode('utf-8'))

#        try:
#            if size_og[0] >= 600:
#               line.add_value('img', img_og.encode('utf-8'))
#            else:
#                try:
#                    img = body_soup.find('meta', attrs={'name' : re.compile(r"twitter:image", re.I)})
#                    img_tw = str(img['content'].encode('utf-8'))
#                    img_tw = re.sub(r' (.*)', '', img_tw)
#                    size_tw = imgSizes(str(img_tw))
#                except:
#                    pass
#                try:
#                    if size_og[0] >= 200:
#                        line.add_value('img', img_og.encode('utf-8'))
#                    elif size_tw[0] > size_og[0] and size_tw[0] >= 200:
#                        line.replace_value('img', img_tw.encode('utf-8'))
#                except:
#                    pass
#        except:
#            pass

        # desciption
        desc = ''
        try:
            desc = body_soup.find('meta', attrs={'property' : re.compile(r"og:description", re.I)})
            desc = str(desc['content'].encode('utf-8'))
        except:
            pass

        if desc == '':
            try:
                desc = body_soup.find('meta', attrs={'property' : re.compile(r"twitter:description", re.I)})
                desc = str(desc['content'].encode('utf-8'))
            except:
                pass   

        key = str(title) + str(desc) + str(domain_url)
        title_domain_id = hashlib.sha1(str(key)).hexdigest()
        line.add_value('sid', title_domain_id)       

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
        try:
            short_url = body_soup.find('meta', attrs={'name' : re.compile(r"short.url(|s)", re.I)})
            short_url = str(short_url['content'].encode('utf-8'))
            line.add_value('short_url', short_url)
        except:
            pass

        # language
        try:
            lang = body_soup.find('html')
            lang = str(lang['lang'].encode('utf-8'))
            line.add_value('lang', lang)
        except:
            pass
            

        # robots
        try:
            robots = body_soup.find('meta', attrs={'name' : re.compile(r"robots", re.I)})
            robots = str(robots['content'].encode('utf-8'))
        except:
            pass



        # date

        # rule to extract date
        date_name_regex = r"(.*?)(?<!vali)date(.*)"
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

        elif body_soup.find(content=re.compile(date_regex_1)):
            found = body_soup.find(content=re.compile(date_regex_1))
            date_rule = '//body/@content'
            date = found['content'].encode('utf-8')

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
        print 'date rule : ' + str(date_rule)
        print date
        print date_matched


        # store date into flat
        if re.match(date_regex_5, date_matched):
            line.replace_value('date', str(date_matched)+' 00:00:00')

        line.add_value('date_rule', str(date_rule))




        # body #1 : by tag regex

        # remove unnecesoory parts of html again : head, foot
        html = re.sub(r'<head(|er)\b[^>]*>(.*?)</head(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<foot(|er)\b[^>]*>(.*?)</foot(|er)>', '', html, flags = re.DOTALL | re.IGNORECASE)

        # store html into soup format again
        #try:
        #    body_soup = BeautifulSoup(html, from_encoding="utf-8")
        #except HTMLParseError, e:
        #    raise e

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
        unlikely_rule = r"today|warning|title|carousel|widget|notice|popular|sns|click|gnb|banner|dncopy3|ad-|ad_|-ad|_ad|next|previous|tools|follow|nav|share|sharing|link|combx|community|disqus|extra|head|header|menu|remark|aggregate|pagination|channel"
        likely_rule = re.compile(r"body|article|content|wrap|description|desc|with|news|blog|post|pos|video|story", flags = re.IGNORECASE)

        for tag in body_soup.find_all(attrs={'class': re.compile(bad_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                print 'bad matched'
                print str(tag['class'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'class': re.compile(unlikely_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                print 'unlikely_matched'
                print str(tag['class'])
                if likely_rule.search(str(tag['class'])):
                    print '-> likely_matched'
                else: 
                    tag.extract()
        for tag in body_soup.find_all(attrs={'id': re.compile(bad_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:            
                print 'bad matched'
                print str(tag['id'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'id': re.compile(unlikely_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                print 'unlikely_matched'
                print str(tag['id'])
                if likely_rule.search(str(tag['id'])):
                    print '-> likely_matched'
                else: 
                    tag.extract()

        for tag in body_soup.find_all(attrs={'name': re.compile(bad_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:            
                print 'bad matched'
                print str(tag['name'])
                tag.extract()
        for tag in body_soup.find_all(attrs={'name': re.compile(unlikely_rule, re.I)}):
            print tag.name
            if tag.name not in ['html', 'body', 'article', 'section']:
                print 'unlikely_matched'
                print str(tag['name'])
                if likely_rule.search(str(tag['name'])):
                    print '-> likely_matched'
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
            print b
            if b == '' or b == ' ':
                pass
            elif len(b) > 140:
                if b not in body_arr_140:
                    #print b
                    body_arr_140.append(b)


        if len(body_arr_140) > 0:
            body_html_from_arr_max = max(body_arr_140, key=len)
            body_html_from_arr_sum = " ".join(body_arr_140)
            body_rule += ' length 140'
        #elif len(body_arr_50) > 0:
        #    if body_rule == '999':
        #        body_html_from_arr = " ".join(body_arr_50)
        #        body_rule += ' length 50'

        if body_rule == '999':
            body_html = desc
        else:
            body_html = body_html_from_arr_max


        # length check
        print 'body rule : ' + str(body_rule)
        body_len = len(str(body_html))
        print "body length = " + str(body_len)
        title_len = len(str(title))

        #body_html = str(body_html).encode('utf-8')

        #body_html_pack = re.sub(r'(^\s+)', '', body_html)

        #print body_html
        
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



        if robots == 'noindex':
            print >> self.url_error, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid], 'banned by robots.txt')

        elif domain_url == 'www.facebook.com' or domain_url == 'm.facebook.com' or domain_url == 'instagram.com':
            body_html = body_html_from_arr_sum
            print 'SNS'
            if body_len > title_len:
                line.add_value('text', body_html)
            else:
                line.add_value('text', title)
            line.replace_value('title', '')
            line.replace_value('body', '')
            yield line.load_item()
            domail_url = ''
            print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid])

        elif title is not None:
            yield line.load_item()
            print >> self.url_out, '%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid]) 

        elif title is None:
            print >> self.url_error, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid], 'no title')
        else:
            print >> self.url_error, '%s\t%s\t%s\t%s\t%s' % (uid, url_origin, NewsSpider.dic_date[uid], NewsSpider.dic_freq[uid], 'unknown error')

