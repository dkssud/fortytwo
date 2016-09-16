# -*- coding: utf-8 -*-

import json
import time
import elasticq
import wikiparse

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":


    # set count vars
    result_count = 1
    counter = 0
    counter_no_page = 0
    counter_redirect = 0
    counter_indexed = 0
    counter_error = 0
    counter_mark = 0
    counter_mark_error = 0

    type_name = str(sys.argv[1])


    # get twt: look up data that miss _indexed field order by date asc
    while (result_count > 0 and counter < 5000):

        # initilize result vars
        search_result = []
        result_dic = {}

        # get wikipedia pages from ES
        search_post_data = json.dumps({"size": 1000, "query": {"bool": {"must_not": {"match": {"_indexed": True}}}}, "sort": {"timestamp": {"order": "desc"}}})
        search_result = elasticq.searchQ('localhost:9200', 'wikipedia', type_name, search_post_data)

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


        for result in result_dic:

            # initialize vars
            counter += 1
            if_page = True
            if_error = False

            # get id & ns
            wiki_id = result['_id']
            result = result['_source']
            ns = result['ns']

            # 
            if int(ns) != 0:
                if_page = False
                counter_no_page += 1
            else:
                key = 'redirect'
                if key in result:
                    if_page = False
                    counter_redirect += 1

            if if_page == True:
                wiki_dic = wikiparse.parseWiki(result, wiki_id, type_name)

                #print wiki_dic['title']
                #print wiki_dic['body']

                update_result = {}
                try:
                    post_data = json.dumps(wiki_dic)
                    #print post_data
                    #update_result = elasticq.putQ('forty.tw:18181', 'tjcl', 'wikipedia', str(wiki_id), post_data)
                    update_result = elasticq.putQ('forty.tw:18181', 'wiki', 'wikipedia'+str(type_name), str(wiki_id), post_data)
                    counter_indexed += 1
                except Exception, e:
                    counter_error += 1
                    if_error = True
                    # log error
                    print "! error occurred while indexing wikipedia"
                    print wiki_id
                    print wiki_dic

            mark_result = {}
            if if_error == False:
                try:
                    mark_post_data = json.dumps({"doc" : {"_indexed" : True}})
                    mark_result = elasticq.updateQ('localhost:9200', 'wikipedia', type_name, str(wiki_id), mark_post_data)
                    counter_mark += 1
                except Exception, e:
                    counter_mark_error += 1
                    # log error
                    print "! error occurred while marking to raw wikipedia"
                    print wiki_id
                    print wiki_dic
                     
        time.sleep(30)
        
    if counter_error == 0 and counter_mark_error == 0:
        print "! no error"

    print "------------"
    print "after indexing wikipedia"
    print "------------"
    print counter, "raw wikis processed"
    print counter_indexed, "indexed"
    print counter_no_page, "no pages"
    print counter_redirect, "redirect pages"
    print counter_error, "errors"
    print "------------"
    print "after marking to raw"
    print "------------"
    print counter_mark, "marked"
    print counter_mark_error, "mark errors"    





           


