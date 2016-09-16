# -*- coding: utf-8 -*-

import bz2
import json
import elasticq
import time

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":

    # set filename and open
    filename = '/srv/_tmp/namuwikiFull.json.bz2'
    f = bz2.BZ2File(filename, 'r')

    # initialize vars
    doc = {}
    wiki_id = None
    counter = 0
    counter_error = 0

    for line in f:
        # strip '['. ']'. ',', '\n'
        line = line.lstrip('[')
        line = line.rstrip('\n')
        line = line.rstrip(']')
        line = line.rstrip(',')


        # make dictionary
        try:
            doc = json.loads(line)
        except:
            print line
            counter_error += 1

        # check 'id' exists or not
        key = 'id'
        if key not in doc:
            pass
        else:
            # get id
            wiki_id = doc['id']


        # index
        if wiki_id != None:
            #print json.dumps(doc)
            update_result = elasticq.putQ('localhost:9200', 'namuwiki', 'document', str(wiki_id), json.dumps(doc))
            counter += 1
        else:
            print line
            counter_error += 1

        # pause
        time.sleep(0.05)


print "--- after indexing namuwiki ---"
print counter, "indexed"
print counter_error, "errors"



