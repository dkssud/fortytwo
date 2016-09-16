# -*- coding: utf-8 -*-

import json
import os
import time
import elasticq

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":

    # open file
    f = open('/srv/_tmp/url.tmp', 'w')
    f_log = open('/srv/_log/crawl.log', 'a')
    f_url_log = open('/srv/_log/get_url.log', 'a')

    # set count vars
    result_count = 1
    counter = 0
    counter_url = 0
    counter_error = 0
    counter_twt = 0
    counter_url_plus = 0


    # make postdata and search : look up data that miss unshorened_url field order by date asc
    while (result_count > 0 and counter < 500):

        # initialize counter vars
        counter_error_tmp = 0
        counter_url_plus_tmp = 0
        
        # initilize result vars
        search_result = []
        result_dic = {}

        # get urls
        search_post_data = json.dumps({"size": 500, "filter" : {"and" : [{"missing" : {"field" : "crawled_date"}}, {"not" : {"term" : {"_duplicated": True}}}]}, "sort": { "freq": { "order": "desc" }}})      
        search_result = elasticq.searchQ('localhost:9200', 'url', 'unshortened', search_post_data)

        # store result and result count
        result_dic = search_result[0]
        result_count = search_result[1]

        # log result count
        if result_count == 0:
            break
        else:
            print >> f_url_log, "%s" % ("------------")
            print >> f_url_log, "%i%s" % (result_count, " input urls")
            print >> f_url_log, "%s" % ("------------")
            #pass

        # store id, url, date
        for result in result_dic:

            # initialize counter vars
            counter += 1
            counter_final = 0

            # initialize vars
            web_id = None
            url = None
            twt_ids = []
            text_id = None
            final_web_id = None
            final_url = None
            if_final_get = False

            # extract id, url
            web_id = result['_id']
            result = result['_source']
            url = result['unshortened_url']
            twt_ids = result['twt_ids']

            # extract text_id
            key = 'text_id'
            if key in result:
                text_id = result[key]

            # mark 1900-01-01 00:00:00 to urls in progress
            mark_crawled_post_data = json.dumps({"doc" : {"crawled_date" : "1900-01-01 00:00:00"}, "doc_as_upsert": False})
            mark_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', web_id, mark_crawled_post_data)            


            # check duplicated urls and gather all

            # initialize twt_ids_list var
            twt_ids_list = []

            # if no text_id, then pass gathering process
            if text_id == None:
                for twt_id in twt_ids:
                    twt_ids_list.append(str(twt_id))

                # choose url as final url
                if_final_get = True
                counter_final += 1
                final_web_id = web_id
                final_url = url

            else:
                # set vars
                get_all_url_result = []
                get_all_url_result_dic = {}
                result_count = 0

                # search url index by text_id to gather urls with same contents
                get_all_url_post_data = json.dumps({"size": 1000, "query": {"match": {"text_id": text_id}}})
                get_all_url_result = elasticq.searchQ('localhost:9200', 'url', 'unshortened', get_all_url_post_data)

                # store search results
                get_all_url_result_dic = get_all_url_result[0]
                result_count = get_all_url_result[1]

                # log matched url count
                if result_count > 1:
                    print >> f_url_log, "%s%i" % ('> matched url count: ', int(result_count))
                    print >> f_url_log, "%s" % (str(get_all_url_result))

                # initialize vars for summation of web ids
                web_id_list = []
                counter_rel_url = 0

                for url_result in get_all_url_result_dic:

                    # count related urls
                    counter_rel_url += 1

                    # initialize vars
                    rel_twt_ids = []
                    rel_web_id = None
                    rel_url = None

                    # extract web_id, url, twt_ids
                    rel_web_id = url_result['_id']
                    url_result = url_result['_source']
                    rel_url = url_result['unshortened_url']
                    rel_twt_ids = url_result['twt_ids']

                    # if unduplicated tweet found, get final_web_id, final_url
                    key = '_duplicated'
                    if key in url_result:
                        if url_result[key] == False:
                            if_final_get = True
                            counter_final += 1
                            final_web_id = web_id
                            final_url = url                            
                    else:
                        if_final_get = True
                        counter_final += 1
                        final_web_id = web_id
                        final_url = url

                    # make uniq id_list of web_id
                    if rel_web_id not in web_id_list:
                        web_id_list.append(rel_web_id)
                    for twt_id in rel_twt_ids:
                        if twt_id not in twt_ids_list:
                            twt_ids_list.append(str(twt_id))

                # log
                if result_count > 1:
                    print >> f_url_log, "%s%s" % ('web_id: ', web_id)
                    print >> f_url_log, "%s%s" % ('url: ', url)

                    if text_id != None:
                        print >> f_url_log, "%s%i" % ('> count of same urls: ', counter_rel_url)
                        print >> f_url_log, "%s%s" % ('web_id_list: ', web_id_list)

                    print >> f_url_log, "%s%s" % ('twt_ids_list: ', twt_ids_list)
                    print >> f_url_log, "%s%i" % ('> count of get final url: ', counter_final)
                    print >> f_url_log, "%s%s" % ('final_web_id: ', final_web_id)
                    print >> f_url_log, "%s%s" % ('final_url: ', final_url)

                    # count urls added
                    counter_url_plus += counter_rel_url
                    counter_url_plus_tmp += counter_rel_url


            # initialize freq var
            freq = 0
            date_timestamp = 0

            for twt_id in twt_ids_list:

                counter_twt += 1

                # get tweet that mentioned url
                tweet_result = {}
                tweet_result = elasticq.getQ('forty.tw:18181', 'tjcl', 'tweet', twt_id)

                # extract tweet data
                key = '_source'
                if key in tweet_result:
                    tweet_result = tweet_result['_source']

                    # sum freq of tweets
                    freq += tweet_result['freq']

                    # extract oldest date of tweets
                    if date_timestamp == 0 or date_timestamp > tweet_result['date_timestamp']:
                        date_timestamp = tweet_result['date_timestamp']
                        date = tweet_result['date']

            if text_id != None and result_count > 1:
                print >> f_url_log, "%s%s" % ('freq: ', freq)
                print >> f_url_log, "%s%s" % ('date: ', date)
                print >> f_url_log, "%s" % "------------"
                
            # make url file to be crawled
            if date != '' and date != None and final_url != None and final_web_id != None and if_final_get == True and counter_final == 1:
                counter_url += 1      
                print >> f, "%s\t%s\t%s\t%s\t%d\t%s" % (str(final_web_id), str(final_url), str(date), date_timestamp, freq, twt_ids_list)
            else:
                # log error
                print >> f_url_log, "%s" % ('! error occurred')
                print >> f_url_log, "%s" % (web_id)
                print >> f_url_log, "%s" % (result)
                print >> f_url_log, "%s%s" % ('date: ', date)
                print >> f_url_log, "%s%s" % ('counter_final: ', counter_final)
                print >> f_url_log, "%s%s" % ('final_url: ', final_url)
                print >> f_url_log, "%s%s" % ('final_web_id: ', final_web_id)
                print >> f_url_log, "%s" % "------------"
                print >> f_log, "%s" % ('! error occurred')
                print >> f_log, "%s" % (web_id)
                print >> f_log, "%s" % (result)
                print >> f_log, "%s%s" % ('date: ', date)
                print >> f_log, "%s%s" % ('counter_final: ', counter_final)
                print >> f_log, "%s%s" % ('final_url: ', final_url)
                print >> f_log, "%s%s" % ('final_web_id: ', final_web_id)
                counter_error += 1
                counter_error_tmp += 1

                for wid in web_id_list:
                    del_post_data = json.dumps({"script": "del-_duplicated"})
                    delete_web_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', wid, del_post_data)
                    delete_web_result = elasticq.updateQ('forty.tw:18181', 'tjcl', 'web', wid, del_post_data)
                    del_post_data = json.dumps({"script": "del-_filtered"})
                    delete_web_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', wid, del_post_data)
                    delete_web_result = elasticq.updateQ('forty.tw:18181', 'tjcl', 'web', wid, del_post_data)
                    del_post_data = json.dumps({"script": "del-crawled_date"})
                    delete_web_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', wid, del_post_data)                             
                    del_post_data = json.dumps({"script": "del-text_id"})
                    delete_web_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', wid, del_post_data)
                    delete_web_result = elasticq.updateQ('forty.tw:18181', 'tjcl', 'web', wid, del_post_data)             

        #time.sleep(30)

        if counter_error_tmp == 0 and counter_url_plus_tmp == 0:
            print >> f_url_log, "%s" % "! no error"
            print >> f_url_log, "%s" % "------------"


    # log after finished
    print >> f_url_log, "%s" % "after get urls"
    print >> f_url_log, "%s" % "------------"
    print >> f_url_log, "%i%s" % (counter, " url inputs")
    print >> f_url_log, "%i%s" % (counter_url_plus, " urls plus")
    print >> f_url_log, "%i%s" % (counter_twt, " tweets related")
    print >> f_url_log, "%i%s" % (counter_url, " urls processed")
    print >> f_url_log, "%i%s" % (counter_error, " errors")

    print >> f_log, "%s" % "------------"
    print >> f_log, "%s" % "after get urls"
    print >> f_log, "%s" % "------------"
    print >> f_log, "%i%s" % (counter, " url inputs")
    print >> f_log, "%i%s" % (counter_url_plus, " urls plus")
    print >> f_log, "%i%s" % (counter_twt, " tweets related")
    print >> f_log, "%i%s" % (counter_url, " urls processed")
    print >> f_log, "%i%s" % (counter_error, " errors")

    # close file
    f.close()
    f_log.close()
    f_url_log.close()




