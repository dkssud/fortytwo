# -*- coding: utf-8 -*-

import datetime
import time

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def parseTwt(twt_dic, idx_from):

    # initialize variables
    media = {}
    expanded_urls = []
    display_urls = []
    media_urls = []
    text = ''
    text_display = ''
    rt_count = 0
    fav_count = 0
    sensitive = False

    # parse twt data
    twt_id = twt_dic['id_str']
    truncated = twt_dic['truncated']
    text = twt_dic['text']
    text_display = text
    created_at = twt_dic['created_at']

    if twt_dic['retweet_count'] != None:
        rt_count = int(twt_dic['retweet_count'])
    if twt_dic['favorite_count'] != None:
        fav_count = int(twt_dic['favorite_count'])
    freq = rt_count + fav_count
    reply_to_id = twt_dic['in_reply_to_status_id_str']

    key = 'possibly_sensitive'
    if key in twt_dic:
        sensitive = twt_dic['possibly_sensitive']

    # parse user data
    user_dic = twt_dic['user']
    user_id = user_dic['id_str']
    user_name = user_dic['name']
    user_screen_name = user_dic['screen_name']
    user_image = user_dic['profile_image_url']

    # parse utc_offset
    utc_offset = user_dic['utc_offset']
    if utc_offset == None:
        utc_offset = 0
    else:
        utc_offset = int(utc_offset)

    # parse entities data
    entities_dic = twt_dic['entities']
    urls = entities_dic['urls']
    hashtags_dic = entities_dic['hashtags']
    mentions_dic = entities_dic['user_mentions']

    # parse extended_entities data
    key = 'extended_entities'
    if key in twt_dic:
        extended_entities_dic = twt_dic['extended_entities']
        media = extended_entities_dic['media']

    # process hashtags and mentions
    hashtags = processTags(hashtags_dic)
    mentions = processMentions(mentions_dic)

    processed = []
    # process urls 
    if urls != []:
        processed = processUrls(text, urls)
        text = processed[0]
        text_display = processed[1]
        expanded_urls = processed[2]
        display_urls = processed[3]

    processed = []
    # process media
    if media != {}:
        processed = processMedia(text, media)
        text = processed[0]
        media_urls = processed[1]
        processed = processMedia(text_display, media)
        text_display = processed[0]

    # process datetime
    created_at = processDatetime(created_at, utc_offset)
    created_at_timestamp = created_at[0]
    created_at_uscentral = created_at[1]
    created_at_local = created_at[2]

    return dict(twt_id=twt_id, idx_from=idx_from, text=text.encode('utf-8'), text_display=text_display.encode('utf-8'), date=created_at_uscentral, date_timestamp=created_at_timestamp, date_local=created_at_local, freq=freq, rt_count=rt_count, fav_count=fav_count, user_id=user_id, user_name=user_name, user_screen_name=user_screen_name, user_image=user_image, original_urls=expanded_urls, target_urls=expanded_urls, display_urls=display_urls, img_urls=media_urls, original_img_urls=media_urls, hashtags=hashtags, mentions=mentions, reply_to_id=reply_to_id, sensitive=sensitive)


def processUrls(text, urls):

    # declare variables
    expanded_url_list = []
    display_url_list = []
    text_display = text

    for u in urls:
        # extract urls
        url = u['url']
        display_url = u['display_url']
        expanded_url = u['expanded_url']

        # make 2 text fields : for display and for search
        text_display = text_display.replace(url, display_url)
        text = text.replace(url, '')

        # make url list : expanded_urls, display_urls
        display_url_list.append(display_url)
        expanded_url_list.append(expanded_url)

    return text, text_display, expanded_url_list, display_url_list


def processMedia(text, media):

    # declare variables
    media_urls = []

    for m in media:
        # replace media_urls in text with blank
        url = m['url']
        text = text.replace(url, '')

        # make media_url list
        media_urls.append(str(m['media_url'])+':large')

    return text, media_urls


def processTags(hashtags):
    # process tags : add #
    tag = []
    for h in hashtags:
        tag.append('#' + str(h['text']))
    return  tag


def processMentions(usermentions):
    # process Mentions : add @
    mentions = []
    for m in usermentions:
        mentions.append('@' + str(m['screen_name']))
    return mentions


def processDatetime(created_at, utc_offset):

    # parse datetime into month, day, year, hour, minute, second
    created_at = created_at.split(' ')
    month = getMonth(created_at[1])
    day = created_at[2]
    year = created_at[5]

    hms = created_at[3]
    hms = hms.split(':')
    hour = hms[0]
    minute = hms[1]
    second = hms[2]

    # convert into unix time
    dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    
    # convert into datetime format
    dt_uscentral = dt.strftime('%Y-%m-%d %H:%M:%S')

    # calculate utc_offset
    ut = time.mktime(dt.timetuple())
    ut = int(ut)
    ut_local = ut + utc_offset

    # convert into datetime format
    dt_local = datetime.datetime.fromtimestamp(int(ut_local)).strftime('%Y-%m-%d %H:%M:%S')
    
    return ut, dt_uscentral, dt_local


def getMonth(month):
    if month == 'Jan':
        return 1
    elif month == 'Feb':
        return 2
    elif month == 'Mar':
        return 3
    elif month == 'Apr':
        return 4
    elif month == 'May':
        return 5
    elif month == 'Jun':
        return 6
    elif month == 'Jul':
        return 7
    elif month == 'Aug':
        return 8
    elif month == 'Sep':
        return 9
    elif month == 'Oct':
        return 10
    elif month == 'Nov':
        return 11
    elif month == 'Dec':
        return 12
