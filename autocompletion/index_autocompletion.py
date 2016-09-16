# -*- coding: utf-8 -*-

import pycurl
import os
import json
from StringIO import StringIO
import hashlib
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

    
def dataInput(filename, typename):

    f = open('/srv/tmp/twt/'+filename)

    count_insert_kw = 0
    count_update_kw = 0
    count_error = 0

    for line in f.readlines():
        line_tab = line.strip().split("\t")
        kw_output = line_tab[0]
        kid = hashlib.sha1(kw_output).hexdigest()
        kw_input = line_tab[1]
        weight = int(line_tab[2])

        postData = json.dumps({"script" : "weight-cal", "params" : {"count" : weight}, "upsert" : {"keyword" : kw_output, "suggest" : {"input" : kw_input, "output" : kw_output, "payload" : {"id" : kid}, "weight" : weight}}}, ensure_ascii=False, separators=(',',':'))
        
        print postData

        result = StringIO()
        dic_result = {}

        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://210.106.62.110:18181/shttl/'+typename+'/'+str(kid)+'/_update')
        c.setopt(pycurl.HTTPHEADER, ['Content-Type : application/x-www-form-urlencoded'])
        c.setopt(pycurl.POSTFIELDS, postData)
        c.setopt(pycurl.CUSTOMREQUEST, 'POST')
        c.setopt(c.WRITEFUNCTION, result.write)
        c.perform()

        result = result.getvalue()
        dic_result = json.loads(result)

        try:
            if dic_result['_version'] == 1:
                count_insert_kw += 1
            else:
                count_update_kw += 1
        except KeyError, e:
            count_error += 1
            print dic_result

            pass

    print "---index "+typename+"---"
    print "%i%s" % (count_insert_kw, " docs inserted",)
    print "%i%s" % (count_update_kw, " docs updated",)
    print "%i%s" % (count_error, " errors occurred",)


if __name__ == "__main__":

    completion = 'completion.txt'

    dataInput(completion, 'completion')
