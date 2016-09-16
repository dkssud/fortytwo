# -*- coding: utf-8 -*-
from StringIO import StringIO
import pycurl
import json

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# functions

def getQ(cluster_name, index_name, type_name, doc_id):

    # declare result variables
    result = StringIO()
    dic_result = {}

    # curl
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://'+str(cluster_name)+'/'+str(index_name)+'/'+str(type_name)+'/'+str(doc_id))
    c.setopt(pycurl.CUSTOMREQUEST, 'GET')
    c.setopt(c.WRITEFUNCTION, result.write)
    c.perform()
    c.close()

    # extract result
    result = result.getvalue()
    dic_result = json.loads(result)

    return dic_result

def putQ(cluster_name, index_name, type_name, doc_id, post_data):

    # declare result variables
    result = StringIO()
    dic_result = {}

    # curl
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://'+str(cluster_name)+'/'+str(index_name)+'/'+str(type_name)+'/'+str(doc_id))
    #c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(pycurl.POSTFIELDS, post_data)
    c.setopt(pycurl.CUSTOMREQUEST, 'PUT')
    c.setopt(c.WRITEFUNCTION, result.write)
    c.perform()
    c.close()

    # extract result
    result = result.getvalue()
    dic_result = json.loads(result)

    return dic_result

    
def searchQ(cluster_name, index_name, type_name, post_data):

	# initialize vars
    result = StringIO()
    result_count = 0
    result_dic = {}
    
    # curl
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://'+str(cluster_name)+'/'+str(index_name)+'/'+str(type_name)+'/_search?query_cache=false')
    c.setopt(pycurl.HTTPHEADER, ['Content-Type : application/x-www-form-urlencoded'])
    c.setopt(pycurl.POSTFIELDS, post_data)
    c.setopt(pycurl.CUSTOMREQUEST, 'POST')
    c.setopt(c.WRITEFUNCTION, result.write)
    c.perform()
    c.close()

    # extract result
    result = result.getvalue()
    result_dic = json.loads(result)
    result_dic = result_dic['hits']
    result_count = result_dic['total']
    result_dic = result_dic['hits']

    # return result dic and result count
    return result_dic, result_count


def updateQ(cluster_name, index_name, type_name, doc_id, post_data):

	# initialize vars
    result = StringIO()
    result_dic = {}
    
    # curl
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'http://'+str(cluster_name)+'/'+str(index_name)+'/'+str(type_name)+'/'+str(doc_id)+'/_update')
    c.setopt(pycurl.HTTPHEADER, ['Content-Type : application/x-www-form-urlencoded'])
    c.setopt(pycurl.POSTFIELDS, post_data)
    c.setopt(pycurl.CUSTOMREQUEST, 'POST')
    c.setopt(c.WRITEFUNCTION, result.write)
    c.perform()
    c.close() 

    # extract result
    result = result.getvalue()
    result_dic = json.loads(result)

    # return result dic
    return result_dic


