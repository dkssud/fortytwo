# -*- coding: utf-8 -*-

import json
import time
import elasticq
import tumblrparse

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":


    # set count vars
    result_count = 1
    counter = 0
    counter_indexed = 0
    counter_error = 0
    counter_mark = 0
    counter_mark_error = 0
    index_name = str(sys.argv[1])
    type_name = str(sys.argv[2])


    # get twt: look up data that miss _indexed field order by date asc
    while (result_count > 0 and counter < 10000):

        # initilize result vars
        search_result = []
        result_dic = {}

        # get tumblr posts from ES
        search_post_data = json.dumps({"size": 1000, "query": {"bool": {"must_not": {"match": {"_indexed": True}}}}, "sort": {"timestamp": {"order": "asc"}}})
        search_result = elasticq.searchQ('localhost:9200', index_name, type_name, search_post_data)

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

            counter += 1
            if_error = False
            if_no_text = False
            text_key = ''

            tumblr_id = result['_id']
            source = result['_source']

            if type_name == 'text':
                tumblr_dic = tumblrparse.parseText(source, tumblr_id, type_name)
            elif type_name == 'photo':
                tumblr_dic = tumblrparse.parsePhoto(source, tumblr_id, type_name)
            elif type_name == 'quote':
                tumblr_dic = tumblrparse.parseQuote(source, tumblr_id, type_name)
            elif type_name == 'link':
                tumblr_dic = tumblrparse.parseLink(source, tumblr_id, type_name)

            elif type_name == 'video':
                tumblr_dic = tumblrparse.parseVideo(source, tumblr_id, type_name)
            elif type_name == 'audio':
                tumblr_dic = tumblrparse.parseAudio(source, tumblr_id, type_name)
            elif type_name == 'chat':
                tumblr_dic = tumblrparse.parseChat(source, tumblr_id, type_name)
            elif type_name == 'answer':
                tumblr_dic = tumblrparse.parseAnswer(source, tumblr_id)
            else:
                sys.exit(0)

            text_key = str(tumblr_dic['title']) + str(tumblr_dic['body'])

            if text_key == '' or text_key == None:
                counter_error += 1
                if_no_text = True
                # log error
                print "! no text"
                print tumblr_id
                print tumblr_dic


            update_result = {}

            if if_no_text == False:
                try:
                    post_data = json.dumps(tumblr_dic)
                    #print post_data
                    update_result = elasticq.putQ('forty.tw:18181', 'tjcl', 'tumblr', str(tumblr_id), post_data)
                    counter_indexed += 1
                except Exception, e:
                    counter_error += 1
                    if_error = True
                    # log error
                    print "! error occurred while indexing tumblr"
                    print tumblr_id
                    print tumblr_dic

            mark_result = {}
            if if_error == False:
                try:
                    mark_post_data = json.dumps({"doc" : {"_indexed" : True}})
                    mark_result = elasticq.updateQ('localhost:9200', index_name, type_name, str(tumblr_id), mark_post_data)
                    counter_mark += 1
                except Exception, e:
                    counter_mark_error += 1
                    # log error
                    print "! error occurred while marking to raw tumblr"
                    print tumblr_id
                    print tumblr_dic           

        time.sleep(30)
        
    if counter_error == 0 and counter_mark_error == 0:
        print "! no error"            
            
        #print counter
        #print counter_post
    print "------------"
    print "after indexing tumblr"
    print "------------"
    print counter_indexed, "posts indexed"
    print counter_error, "errors"
    print counter_mark, "marked"
    print counter_mark_error, "mark errors"






