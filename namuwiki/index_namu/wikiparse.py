# -*- coding: utf-8 -*-

import re
import time
import datetime
import urllib

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# get img module : need to exract img link not img-page link
def parseImg(body, url):

    # initialize vars
    matched = []
    img_urls = []
    img = ''

    # img regex
    img_regex_1 = r"\= (.*?)(\.jpg|\.png|\.gif|\.swf)"
    img_regex_2 = r"\[\[(file|파일):(.*?)(\.jpg|\.png|\.gif|\.swf)"

    # for regex_1
    if re.search(img_regex_1, body):
        matched = re.findall(img_regex_1, body)
        for m in matched:
            for t in m:
                t = t.replace(' ', '_')
                img += str(t)
            img_urls.append(img)

    # for regex_2
    if re.search(img_regex_2, body):
        matched = re.findall(img_regex_2, body)
        for m in matched:
            for t in m:
                t = t.replace(' ', '_')
                img += str(t)
            img_urls.append(img)

    # return img_urls
    return img_urls


def parseBody(body):

    # remove tag and ref
    body = re.sub(r'<ref>(.*?)<\/ref>', '', body)
    body = re.sub(r'<[^\b](.*?)>', '', body)

    # extract text inside {{ }}
    body = re.sub(r'{{(llang|lang|ja-y)\|(.*?)}}', r'\2', body)

    # remove inner & outer {{ }} (twice) 
    body = re.sub(r'{{[^{{]*?}}?', '', body)
    body = re.sub(r'{{[^{{]*?}}?', '', body)

    # remove {{ }} again (greedy)
    body = re.sub(r'{{.*?}}', '', body, flags = re.DOTALL)


    # extract text inside [[ ]]
    body = re.sub(r'\[\[File:([^\[\[]*?)\]\]', '', body)
    body = re.sub(r'\[\[([^\[\[]*?)\|([^\[\[]*?)\]\]', r'\1', body)

    # remove {| |} __
    body = re.sub(r'{\|(.*?)\|}', '', body)
    body = re.sub(r'{\|(.*?)\|}', '', body, flags = re.DOTALL)
    body = re.sub(r'__(.*?)__', '', body)
    body = re.sub(r'__(.*?)__', '', body, flags = re.DOTALL)

    # process repeated special characters
    body = re.sub(r'\=+', '=', body)
    body = re.sub(r'\*+', '*', body)

    # remove other special characters
    body = body.replace('[[','')
    body = body.replace(']]','')
    body = body.replace('=','')
    body = body.replace('*','-')
    body = body.replace('\'\'\'', '\'')

    # remove new line
    body = re.sub(r'\n\n+', r'\n', body)

    return body


def parseWiki(wiki_dic, wiki_id, wiki_type):

    # initialize variables
    title = ''
    body = ''
    freq = 0
    date = None
    domain = ''
    url = None
    urls = []
    img_urls = []

    # get title, body
    title = wiki_dic['title']
    wiki_dic = wiki_dic['revision']
    body = wiki_dic['text']['#text']
    body = parseBody(body)

    # get date and convert to unixtime
    date = wiki_dic['timestamp']
    date = date.replace('T', ' ')
    date = date.replace('Z', '')
    timestamp = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple()))

    # get freq by calculating length of text
    freq = int(len(body)*0.1)

    # get domain & url
    domain = str(wiki_type) + '.wikipedia.org'
    url_title = title.replace(' ', '_')
    url = 'http://' + domain + '/wiki/' + str(url_title)
    #url = urllib.quote(url, '/:#?&=_%')
    if url != None:
        urls.append(url)

    # add 'Wikipedia' to title
    if title != '':
        title += ' - Wikipedia'

    # get img
    #img_urls = parseImg(body, url)


    # return parsed data
    return dict(wiki_id=wiki_id, wiki_type=wiki_type, title=title.encode('utf-8'), wiki_body=body.encode('utf-8'), freq=freq, date_timestamp=timestamp, date=date, domain=domain, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls)


def parseNamuBody(body):

    # initialize vars
    img_urls = []
    img = ''

    # extract image
    img_regex_1 = r'(\[http|http|https)(:\/\/)(.+)(\.)(jpg\?[^\s]+|jpg[^\s]|jpg|png\?[^\s]+|png[^\s]|png|gif\?[^\s]+|gif[^\s]|gif|swf\?[^\s]+|swf[^\s]|swf|jpeg\?[^\s]+|jpeg[^\s]|jpeg)'
    if re.search(img_regex_1, body, flags=re.I):
        matched = re.findall(img_regex_1, body, flags=re.I)
        for m in matched[0]:
            img += str(m)
        img_urls.append(img)

        body = re.sub(r'(\[http|http|https)(:\/\/)(.+)(\.)(jpg\?[^\s]+|jpg[^\s]|jpg|png\?[^\s]+|png[^\s]|png|gif\?[^\s]+|gif[^\s]|gif|swf\?[^\s]+|swf[^\s]|swf|jpeg\?[^\s]+|jpeg[^\s]|jpeg)', '', body, flags=re.I)

    # remove tag and ref
    body = body.encode('utf-8')
    body = re.sub(r'\[\[(목차|각주)\]\]', '', body)
    body = re.sub(r'== (개요|소개) ==', '', body)
    body = re.sub(r'= (개요|소개) =', '', body)
    body = re.sub(r'\* 상위 항목 : (.*)', '', body)
    body = re.sub(r'\[\[include\(틀:(.*)\]\]', '', body, flags = re.I)

    body = re.sub(r'\[wiki:\"(.*?)\"(.*?)\]', r'\2', body)
    body = re.sub(r'\[\"(.*?)\"(.*?)\]', r'\2', body)
    body = re.sub(r'\[\[(.*?)\|(.*?)\]\]', r'\2', body)
    body = re.sub(r'\[(.*?)\|(.*?)\]', r'\2', body)
    body = re.sub(r'attachment:(.*)', '', body, flags = re.I)

    body = re.sub(r'\|\|(.*)\|\|', '', body)

    body = re.sub(r'<[^\b](.*?)>', '', body)

    # extract text inside {{ }}
    #body = re.sub(r'{{(llang|lang|ja-y)\|(.*?)}}', r'\2', body)

    # remove inner & outer {{ }} (twice) 
    body = re.sub(r'{{{[^{{{]*?}}}?', '', body)
    body = re.sub(r'{{{[^{{{]*?}}}?', '', body)
    body = re.sub(r'{{[^{{]*?}}?', '', body)
    body = re.sub(r'{{[^{{]*?}}?', '', body)

    # remove {{ }} again (greedy)
    #body = re.sub(r'{{.*?}}', '', body, flags = re.DOTALL)


    # extract text inside [[ ]]
    #body = re.sub(r'\[\[File:([^\[\[]*?)\]\]', '', body)
    #body = re.sub(r'\[\[([^\[\[]*?)\|([^\[\[]*?)\]\]', r'\1', body)

    # remove {| |} __
    #body = re.sub(r'{\|(.*?)\|}', '', body)
    #body = re.sub(r'{\|(.*?)\|}', '', body, flags = re.DOTALL)
    #body = re.sub(r'__(.*?)__', '', body)
    #body = re.sub(r'__(.*?)__', '', body, flags = re.DOTALL)

    # process repeated special characters
    body = re.sub(r'\=+', '=', body)
    body = re.sub(r'\*+', '*', body)

    # remove other special characters
    body = body.replace('[[br]]','')
    body = body.replace('[[','')
    body = body.replace(']]','')
    body = body.replace('[]','')
    body = body.replace(']]','')
    body = body.replace(']]','')
    body = body.replace('~~','')
    body = body.replace('--','')
    body = body.replace('||','')
    body = body.replace('>','')

    body = body.replace('[','(')
    body = body.replace(']',')')
    body = body.replace('=','')
    body = body.replace('*','-')
    body = body.replace('\'\'\'', '')

    # remove new line
    body = re.sub(r'\n\n+', r'\n', body)
    body = re.sub(r'\s\s+', r' ', body)

    body = body.lstrip('\n\t\b')
    body = body.lstrip(' ')
    body = body.rstrip('\n\t\b')
    body = body.rstrip(' ')

    return body, img_urls

def parseNamu(wiki_dic, wiki_id, wiki_type):

    # initialize variables
    title = ''
    body = ''
    parsed_body = []
    freq = 0
    date = 0
    timestamp = 0
    date_string = ''
    domain = ''
    url = None
    urls = []
    img_urls = []

    # get title, body
    title = wiki_dic['document']
    body = wiki_dic['text']
    parsed_body = parseNamuBody(body)
    body = parsed_body[0]
    img_urls = parsed_body[1]

    # get date and convert to unixtime
    date = wiki_dic['date']
    timestamp = date
    rev = wiki_dic['rev']
    date_string = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    # get freq by calculating length of text
    freq = int(len(body)*0.1)

    # get domain & url
    domain = 'namu.wiki'
    url = 'http://' + domain + '/w/' + str(title)
    #url = urllib.quote(url, '/:#?&=_%')
    if url != None:
        urls.append(url)

    # add 'Wikipedia' to title
    if title != '':
        title += ' - 나무위키'

    # get img
    #img_urls = parseImg(body, url)


    # return parsed data
    return dict(wiki_id=wiki_id, wiki_type=wiki_type, title=title.encode('utf-8'), wiki_body=body.encode('utf-8'), freq=freq, date_timestamp=timestamp, date=date_string, domain=domain, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls)



