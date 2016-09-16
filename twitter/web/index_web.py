# -*- coding: utf-8 -*-

import os
import json
import elasticq

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

    
def dataInput(filename):

    f = open('/srv/_tmp/'+filename)
    f_log = open('/srv/_log/crawl.log', 'a')
    #f_error = open('/srv/twitter/_log/crawl_index_error.log', 'a')
    #f_mark_error = open('/srv/twitter/_log/crawl_mark_error.log', 'a')

    # set vars
    counter_indexed_freq = 0
    counter_indexed = 0
    counter_insert_freq = 0
    counter_insert = 0
    counter_update_freq = 0
    counter_update = 0
    counter_error_freq = 0
    counter_error = 0
    counter_mark = 0
    counter_mark_error = 0
    counter_mark_filtered = 0
    counter_mark_filtered_error = 0


    for line in f.readlines():

        # extract ID
        data = json.loads(line)
        web_id = data['web_id']

        freq = 0
        date_timestamp = 0
        twt_ids = []

        # convert type of freq to integer
        freq = int(data['freq'])
        data['freq'] = freq
        date_timestamp = int(data['date_timestamp'])
        data['date_timestamp'] = date_timestamp
        crawled_date = data['crawled_date']
        twt_ids = data['twt_ids']
 
        # initialize vars
        update_result = {}
        if_error = False

        # set post data
        #update_post_data = json.dumps({"script" : "web-freq-cal", "params" : {"count" : freq}, "upsert" : data})
        
        # index to tjcl
        try:
            update_result = elasticq.putQ('forty.tw:18181', 'tjcl', 'web', str(web_id), json.dumps(data))
            counter_indexed += 1
            counter_indexed_freq += freq

        except Exception, e:
            if_error = True
            # log error
            print >> f_log, "%s" % ("! error occurred while update to tjcl")
            print >> f_log, "%s" % (web_id)
            print >> f_log, "%s" % (data)
            counter_error += 1
            counter_error_freq += freq


        # check whether insert or update
        if if_error == False:
            key = 'error'
            if key not in update_result:
                if update_result['_version'] == 1:
                    counter_insert_freq += freq
                    counter_insert += 1
                else:
                    counter_update_freq += freq
                    counter_update += 1

            else:
                # log error
                if_error = True
                print >> f_log, "%s" % ("! error occurred while update to tjcl")
                print >> f_log, "%s" % (web_id)
                print >> f_log, "%s" % (data)
                print >> f_log, "%s" % (update_result)
                counter_error += 1
                counter_error_freq += freq

        # mark 'crawled_date' in urls
        if if_error == False:
            mark_post_data = json.dumps({"doc": {"crawled_date": crawled_date}})
            try:
                mark_result = elasticq.updateQ('localhost:9200', 'url', 'unshortened', str(web_id), mark_post_data)
                counter_mark += 1
            except Exception, e:
                counter_mark_error += 1
                print >> f_log, "%s" % ("! error occurred while marking to url")
                print >> f_log, "%s" % (web_id)
                print >> f_log, "%s" % (data)
                print >> f_log, "%s" % (mark_post_data)

        for twt_id in twt_ids:
            mark_filtered_post_data = json.dumps({"doc": {"_crawled": True}})
            try:
                mark_filtered_result = elasticq.updateQ('forty.tw:18181', 'tjcl', 'tweet', str(twt_id), mark_filtered_post_data)
                counter_mark_filtered += 1
            except Exception, e:
                counter_mark_filtered_error += 1
                print >> f_log, "%s" % ("! error occurred while marking '_crawled' to tweet")
                print >> f_log, "%s" % (web_id)
                print >> f_log, "%s" % (data)
                print >> f_log, "%s" % (mark_filtered_post_data)

    # log after indexing
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "after indexing web"
    print >> f_log, "%s" % ("after indexing web",)
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "%i%s" % (counter_insert, " inserted",)
    print >> f_log, "%i%s" % (counter_insert, " inserted",)
    print "%i%s" % (counter_insert_freq, " freq of inserted",)
    print >> f_log, "%i%s" % (counter_insert_freq, " freq of inserted",)
    print "%i%s" % (counter_update, " updated",)
    print >> f_log, "%i%s" % (counter_update, " updated",)
    print "%i%s" % (counter_update_freq, " freq of updated",)
    print >> f_log, "%i%s" % (counter_update_freq, " freq of updated",)
    print "%i%s" % (counter_error, " errors",)
    print >> f_log, "%i%s" % (counter_error, " errors",)
    print "%i%s" % (counter_error_freq, " freq of errors",)
    print >> f_log, "%i%s" % (counter_error_freq, " freq of errors",)
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "after marking to url"
    print >> f_log, "%s" % ("after marking to url",)
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "%i%s" % (counter_mark, " marked",)
    print >> f_log, "%i%s" % (counter_mark, " marked",)
    print "%i%s" % (counter_mark_error, " mark errors",)
    print >> f_log, "%i%s" % (counter_mark_error, " mark errors",)
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "after marking to tweet"
    print >> f_log, "%s" % ("after marking to tweet",)
    print "------------"
    print >> f_log, "%s" % ("------------",)
    print "%i%s" % (counter_mark_filtered, " marked",)
    print >> f_log, "%i%s" % (counter_mark_filtered, " marked",)
    print "%i%s" % (counter_mark_filtered_error, " mark errors",)
    print >> f_log, "%i%s" % (counter_mark_filtered_error, " mark errors",)
    
    f.close()
    f_log.close() 

if __name__ == "__main__":

    input_file = 'web.json'

    dataInput(input_file)

