# -*- coding: utf-8 -*-

import string

if __name__=="__main__":

    crawl_error = open("/srv/_tmp/crawl_check.tmp", 'w')

    col_in = []
    col_out = []
    out = []

    f_in = open("/srv/_tmp/url.tmp")
    f_out = open("/srv/_tmp/spider_url.txt")

    for o in f_out.readlines():
        str_out = []
        url_out = ''
        o = o.rstrip('\n')
        col_out = o.split('\t')
        str_out.append(col_out[0])
        str_out.append(col_out[1])
        str_out.append(col_out[2])
        str_out.append(col_out[3])
        url_out = ('\t').join(str_out)
        out.append(url_out)

    for i in f_in.readlines():
        str_in = []
        url_in = ''
        i = i.rstrip('\n')
        col_in = i.split('\t')
        str_in.append(col_in[0])
        str_in.append(col_in[1])
        str_in.append(col_in[2])
        str_in.append(col_in[4])
        url_in = ('\t').join(str_in)

        if url_in not in out:
            print >> crawl_error, '%s' % (url_in)

    f_in.close()
    f_out.close()


