#!/bin/bash

echo "--- total tweets with unshortened_urls ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"filter" : {"exists" : {"field" : "unshortened_urls"}}}}}}'

echo "--- unchanged ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"query" : {"bool": {"must_not": {"match": {"_updated": true}}}}, "filter" : {"exists" : {"field" : "unshortened_urls"}}}}}'

echo "--- newly updated ---"
curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"filtered": {"query" : {"match" : {"_updated" : true}}, "filter" : {"exists" : {"field" : "unshortened_urls"}}}}}}'