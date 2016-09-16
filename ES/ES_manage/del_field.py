# -*- coding: utf-8 -*-

import json
import os
import elasticq
import time

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":

    # set vars
    result_dic = {}
    result_count = 1
    counter = 0

    # key inputs : field, cluster_name, index_name, type_name
    field = str(raw_input("select field > "))
    cluster_name = str(raw_input("select where > "))
    index_name = str(raw_input("select index > "))
    type_name = str(raw_input("select type > "))

    # set cluster_name
    if cluster_name == 'ft':
        cluster_name = 'forty.tw:18181'
    elif cluster_name == 'zb':
        cluster_name = 'localhost:9200'


    # make postdata and search : look up data that miss unshorened_url field order by date asc
    while (result_count > 0 and counter < 50000):

        # get search_result to process
        search_result = []
        post_data = json.dumps({"size": 1000, "filter": {"exists": {"field": field}}})
        search_result = elasticq.searchQ(cluster_name, index_name, type_name, post_data)

        # store search_result
        result_dic = search_result[0]
        result_count = search_result[1]

        for result in result_dic:
            counter += 1

            # set values for deleting
            update_cluster_name = cluster_name
            update_index_name = result['_index']
            update_type_name = type_name
            doc_id = result['_id']
            
            # set script
            script = "del-"+str(field)
            post_data = json.dumps({"script" : script})

            # delete field
            delete_result = {}
            delete_result = elasticq.updateQ(cluster_name, update_index_name, update_type_name, doc_id, post_data)
            print delete_result

        #time.sleep(30)
        
    # log
    print counter, "deleted"










