# -*- coding: utf-8 -*-

import re

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def parseAll(tumblr_dic):

    # initialize vars
    freq = 0
    user = ''
    date = ''
    timestamp = 0
    url = None
    urls = []

    # user
    user = tumblr_dic['blog_name']
    # freq
    key = 'note_count'
    if key in tumblr_dic:
        freq = tumblr_dic[key]
    else:
        freq = 0
    # url
    url = tumblr_dic['post_url']
    if url != None:
        urls.append(str(url))
    # date
    timestamp = tumblr_dic['timestamp']
    date = tumblr_dic['date']
    date = date.rstrip(' GMT')

    return user, date, timestamp, freq, urls

def parseText(tumblr_dic, tumblr_id, type_name):

    # get default values : user, freq, date, timestamp
    get_first = []
    get_first = parseAll(tumblr_dic)

    user = get_first[0]
    date = get_first[1]
    timestamp = get_first[2]
    freq = get_first[3]
    urls = get_first[4]

    # initialize variables
    title = ''
    body = ''
    body_raw =''
    tags = []

    # get title, body, tags
    title = tumblr_dic['title']
    body = tumblr_dic['body']
    tags = tumblr_dic['tags']
    if tags != []:
        body += ' - tags:'
        for tag in tags:
            body += ' #'
            body += str(tag)

    # initialize list for urls and img_urls
    img_urls = []
    post_trail = []
    matched = []

    # find body_raw
    key = 'trail'
    if key in tumblr_dic:
        post_trail = tumblr_dic[key]
        if len(post_trail) > 0:
            i = 0
            while (i < len(post_trail)):
                key = 'content_raw'
                if key in post_trail[i]:
                    body_raw = tumblr_dic['trail'][i][key]
                i += 1

            # find img urls in body raw using regex
            img_regex_1 = r"<img src=\"(.*?)\""
            img_regex_2 = r"image\" src=\"(.*?)\""
            if re.search(img_regex_1, body_raw):
                matched = re.findall(img_regex_1, body_raw)
                for m in matched:
                    img_urls.append(str(m))
            if re.search(img_regex_2, body_raw):
                matched = re.findall(img_regex_2, body_raw)
                for m in matched:
                    img_urls.append(str(m))

    # return parsed data
    return dict(tumblr_id=tumblr_id, tumblr_type=type_name, title=title.encode('utf-8'), body=body.encode('utf-8'), tags=tags, freq=freq, date_timestamp=timestamp, date=date, user_name=user, domain=user, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls)


def parsePhoto(tumblr_dic, tumblr_id, type_name):

    # get default values : user, freq, date, timestamp
    get_first = []
    get_first = parseAll(tumblr_dic)

    user = get_first[0]
    date = get_first[1]
    timestamp = get_first[2]
    freq = get_first[3]
    urls = get_first[4]

    # initialize vars
    title = ''
    body = ''
    photos = []
    img_urls = []
    #width = []
    tags = []

    # get caption, photo url, photo width
    body = tumblr_dic['caption']
    photos = tumblr_dic['photos']

    if len(photos) > 0:
        for photo in photos:
            body += ' '
            body += photo['caption']
            photo = photo['original_size']
            img_urls.append(str(photo['url']))
            #width.append(int(photo['width']))
    
    # get tags and add to body
    tags = tumblr_dic['tags']
    if tags != []:
        body += ' - tags:'
        for tag in tags:
            body += ' #'
            body += str(tag)

    # return parsed data
    return dict(tumblr_id=tumblr_id, tumblr_type=type_name, title=title.encode('utf-8'), body=body.encode('utf-8'), tags=tags, freq=freq, date_timestamp=timestamp, date=date, user_name=user, domain=user, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls)


def parseQuote(tumblr_dic, tumblr_id, type_name):

    # get default values : user, freq, date, timestamp
    get_first = []
    get_first = parseAll(tumblr_dic)

    user = get_first[0]
    date = get_first[1]
    timestamp = get_first[2]
    freq = get_first[3]
    urls = get_first[4]

    # initialize vars
    title = ''
    body = ''
    img_urls = []
    tags = []

    # get title
    key = 'title'
    if key in tumblr_dic:
        title = tumblr_dic[key]

    # get body from text and source
    body = tumblr_dic['text']
    key = 'source'
    if key in tumblr_dic:
        body += ' - '
        body += tumblr_dic['source']

    # get tags and add to body
    tags = tumblr_dic['tags']
    if tags != []:
        body += ' - tags:'
        for tag in tags:
            body += ' #'
            body += str(tag)

    # return parsed data
    return dict(tumblr_id=tumblr_id, tumblr_type=type_name, title=title.encode('utf-8'), body=body.encode('utf-8'), tags=tags, freq=freq, date_timestamp=timestamp, date=date, user_name=user, domain=user, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls)


def parseLink(tumblr_dic, tumblr_id, type_name):

    # get default values : user, freq, date, timestamp
    get_first = []
    get_first = parseAll(tumblr_dic)

    user = get_first[0]
    date = get_first[1]
    timestamp = get_first[2]
    freq = get_first[3]
    urls = get_first[4]

    # initialize vars
    title = ''
    body = ''
    img_urls = []
    tags = []
    url = None
    link_urls = []

    # get title
    key = 'title'
    if key in tumblr_dic:
        title = tumblr_dic[key]

    # get body from description
    body = tumblr_dic['description']

    # get tags and add to body
    tags = tumblr_dic['tags']
    if tags != []:
        body += ' - tags:'
        for tag in tags:
            body += ' #'
            body += str(tag)

    # get link url
    url = tumblr_dic['url']
    if url != None:
        link_urls.append(str(url))

    # find body_raw
    key = 'trail'
    if key in tumblr_dic:
        post_trail = tumblr_dic[key]
        if len(post_trail) > 0:
            i = 0
            while (i < len(post_trail)):
                key = 'content_raw'
                if key in post_trail[i]:
                    body_raw = tumblr_dic['trail'][i][key]
                i += 1

            # find img urls in body raw using regex
            img_regex_1 = r"<img src=\"(.*?)\""
            img_regex_2 = r"image\" src=\"(.*?)\""
            if re.search(img_regex_1, body_raw):
                matched = re.findall(img_regex_1, body_raw)
                for m in matched:
                    img_urls.append(str(m))
            if re.search(img_regex_2, body_raw):
                matched = re.findall(img_regex_2, body_raw)
                for m in matched:
                    img_urls.append(str(m))

    # return parsed data
    return dict(tumblr_id=tumblr_id, tumblr_type=type_name, title=title.encode('utf-8'), body=body.encode('utf-8'), tags=tags, freq=freq, date_timestamp=timestamp, date=date, user_name=user, domain=user, original_urls=urls, target_urls=urls, img_urls=img_urls, original_img_urls=img_urls, link_urls=link_urls)



