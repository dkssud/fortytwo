# -*- coding: utf-8 -*-

import xmltodict
import bz2
import json
import elasticq

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def handle_article(_, article):

    # initialize vars
    wiki_id = None

    # make dict and json
    article_dict = dict(article)
    article = json.dumps(article)

    # check 'id' exists or not
    key = 'id'
    if key not in article:
        pass
    else:
        # get id
        wiki_id = article_dict[key]
        update_result = {}

        #print article
        #print wiki_id

        # update to ES
        if wiki_id != None:
            update_result = elasticq.putQ('localhost:9200', 'wikipedia', str(sys.argv[1]), str(wiki_id), article)
    
    return True


if __name__ == "__main__":

    # select 'ko' or 'en'
    type_name = str(sys.argv[1])
    if type_name == 'ko':
        filename = '/srv/_tmp/kowiki-latest-pages-articles.xml.bz2'
    elif type_name == 'en':
        filename = '/srv/_tmp/enwiki-latest-pages-articles.xml.bz2'
    else:
        sys.exit(0)

    # xmltodict parser streaming
    xmltodict.parse(bz2.BZ2File(filename, 'r'), item_depth=2, item_callback=handle_article)



