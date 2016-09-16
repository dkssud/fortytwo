# -*- coding: utf-8 -*-

import json
import elasticq
import tweetparse

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":

    # set count vars
    result_count = 1
    counter = 0
    counter_error = 0
    counter_insert = 0
    counter_update = 0
    counter_mark = 0
    counter_mark_error = 0
    cluster_name = str(sys.argv[1])


    # get twt: look up data that miss _indexed field order by date asc
    while (result_count > 0 and counter < 5000):

        # initilize result vars
        search_result = []
        result_dic = {}

        # get tweets from ES
        search_post_data = json.dumps({"size": 1000, "query": {"bool": {"must_not": {"match": {"_indexed": True}}}}, "sort": {"timestamp_ms": {"order": "asc"}}})
        search_result = elasticq.searchQ(cluster_name, '*', 'status', search_post_data)

        # store result and result count
        result_dic = search_result[0]
        result_count = search_result[1]

        # log result count
        if result_count == 0:
            break
        else:
            #print result_count, "input twts"
            #print "------------"
            pass


        # parsing
        for result in result_dic:
            counter += 1
            if_error = False

            # extract id, index and result source
            idx_from = result['_index']
            id_from = result['_id']
            source = result['_source']

            # check whether retweeted or not and parse tweets
            key ='retweeted_status'
            twt_dic = {}
            if key in source:
                source_rt = source['retweeted_status']
                twt_dic = tweetparse.parseTwt(source_rt, idx_from)
            else:
                twt_dic = tweetparse.parseTwt(source, idx_from)

            # get tweet id and initialize vars
            twt_id = twt_dic['twt_id']
            update_result = {}           
            
            # set vaule to index to ES(ft)
            update_post_data = json.dumps({"script" : "twt-freq-cal", "params" : {"count": twt_dic['freq'], "rt": twt_dic['rt_count'], "fav" : twt_dic['fav_count']}, "upsert" : twt_dic})

            # index
            try:
                update_result = elasticq.updateQ('forty.tw:18181', 'tjcl', 'tweet', twt_id, update_post_data)
            except Exception, e:
                counter_error += 1
                if_error = True
                # log error
                print "! error occurred while indexing tweet"
                print twt_id
                print twt_dic
                print idx_from

            # check insert, update error
            if if_error == False:
                key = 'error'
                if key not in update_result:
                    if update_result['_version'] == 1:
                        counter_insert += 1
                    else:
                        counter_update += 1
                else:
                    counter_error += 1
                    if_error = True
                    # log error
                    print "! error occurred while indexing tweet"
                    print twt_id
                    print update_result
                    print twt_dic
                    print idx_from


            # mark '_indexed' in raw tweets
            mark_result = {}
            if if_error == False:
                try:
                    mark_post_data = json.dumps({"doc" : {"_indexed" : True}})
                    mark_result = elasticq.updateQ(cluster_name, str(idx_from), 'status', str(id_from), mark_post_data)
                    counter_mark += 1
                    #print "mark", mark
                except Exception, e:
                    counter_mark_error += 1
                    # log error
                    print "! error occurred while marking to raw tweets"
                    print twt_id
                    print twt_dic
                    print idx_from

    if counter_error == 0 and counter_mark_error == 0:
        print "! no error"

    # log after finished
    print "------------"
    print "after indexed"
    print "------------"
    print counter, "raw tweets processed"
    print counter_insert, "inserted"
    print counter_update, "updated"
    print counter_error, "errors"
    print counter_mark, "marked"
    print counter_mark_error, "mark errors"




