#!/bin/bash
if [ "$1" = "t" ]
then
	type_name="tweet"
elif [ "$1" = "w" ]
then
	type_name="web"
else
	exit
fi

echo "--- total tweets with imgs ---"
curl -XPOST forty.tw:18181/tjcl/$type_name/_count?pretty -d '{"query": {"filtered": {"filter" : {"exists" : {"field" : "original_img_urls"}}}}}}'

echo "--- cached ---"
curl -XPOST forty.tw:18181/tjcl/$type_name/_count?pretty -d '{"query": {"filtered": {"query": {"bool": {"must": {"match": {"_img_cached": true}}}}, "filter": {"exists": {"field": "cached_img_urls"}}}}}'

echo "--- failed ---"
curl -XPOST forty.tw:18181/tjcl/$type_name/_count?pretty -d '{"query": {"filtered": {"query": {"bool": {"must": {"match": {"_img_cached": true}}}}, "filter": {"missing": {"field": "cached_img_urls"}}}}}'

echo "--- waiting ---"
curl -XPOST forty.tw:18181/tjcl/$type_name/_count?pretty -d '{"query": {"filtered": {"query" : {"bool": {"must_not": {"match": {"_img_cached": true}}}}, "filter": {"exists" : {"field" : "original_img_urls"}}}}}'