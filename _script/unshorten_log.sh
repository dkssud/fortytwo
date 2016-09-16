#!/bin/bash

echo "--- total twts with urls ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"filter" : {"exists" : {"field" : "original_urls"}}}}}}'

echo "--- unshortened ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"query": {"bool": {"must_not": {"match": {"unshortened_urls": "retry"}}}}, "filter": {"exists": {"field": "unshortened_urls"}}}}}'

echo "--- failed ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"match": {"unshortened_urls": "retry"}}}'

echo "--- waiting ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"filter" : {"and" : [{"missing" : {"field" : "unshortened_urls"}}, {"exists" : {"field" : "original_urls"}}]}}}}}'

if [ "$1" = "a" ]
then 
	echo "--- uniq unshortened ---"
	curl -XGET localhost:9200/url/unshortened/_count?pretty
fi