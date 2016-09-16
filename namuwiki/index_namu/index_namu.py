# -*- coding: utf-8 -*-

import json
import time
import elasticq
import wikiparse
import re

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":


    # set count vars
    result_count = 1
    counter = 0
    counter_redirect = 0
    counter_indexed = 0
    counter_error = 0
    counter_mark = 0
    counter_mark_error = 0


    # get twt: look up data that miss _indexed field order by date asc
    while (result_count > 0 and counter < 2000):

        # initilize result vars
        search_result = []
        result_dic = {}

        # get wikipedia pages from ES
        search_post_data = json.dumps({"size": 1000, "query": {"bool": {"must_not": {"match": {"_indexed": True}}}}, "sort": {"date": {"order": "desc"}}})
        search_result = elasticq.searchQ('localhost:9200', 'namuwiki', 'document', search_post_data)

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
            if_error = False
            if_page = False
            body = ''

            # get id & body
            wiki_id = result['_id']
            result = result['_source']
            body = result['text']

            # check redirect page or not
            redirect_regex = re.compile(r'#redirect(.*)', re.I)
            if re.match(redirect_regex, body):
                counter_redirect += 1
            else:
                if_page = True


            # parse wiki doc
            if if_page == False:
                print result

            else:
                wiki_dic = wikiparse.parseNamu(result, wiki_id, 'namuwiki')

                update_result = {}
                try:
                    post_data = json.dumps(wiki_dic)
                    #print post_data
                    update_result = elasticq.putQ('forty.tw:18181', 'wiki', 'namuwiki', str(wiki_id), post_data)
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
                    mark_result = elasticq.updateQ('localhost:9200', 'namuwiki', 'document', str(wiki_id), mark_post_data)
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
    print "after indexing namuwiki"
    print "------------"
    print counter, "raw wikis processed"
    print counter_indexed, "indexed"
    print counter_redirect, "redirect pages"
    print counter_error, "errors"
    print "------------"
    print "after marking to raw"
    print "------------"
    print counter_mark, "marked"
    print counter_mark_error, "mark errors"    





           


