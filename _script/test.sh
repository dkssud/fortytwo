#!/bin/bash

query=$1

#curl -XGET forty.tw:18181/tjcl/web/_search?pretty -d '{"filter": {"and": [{"term": {"text_id": "'"$query"'", "_cache": false}}, {"not": {"term": {"_duplicated": true, "_cache": false}}}]}, "sort": {"date_timestamp": {"order": "asc"}}}'
#curl -XGET forty.tw:18181/tjcl/web/_search?pretty -d '{"filter": {"term": {"text_id": "'"$query"'", "_cache": false}}, "sort": {"date_timestamp": {"order": "asc"}}}'


curl -XGET localhost:9200/url/unshortened/_search?pretty -d '{"filter": {"and": [{"not": {"term": {"_duplicated": true, "_cache": false}}}, {"missing": {"field": "crawled_date"}}]}, "sort": {"freq": {"order": "desc"}}}'