#!/bin/bash
echo "--- total urls ---"
curl -XPOST localhost:9200/url/unshortened/_count?pretty -d '{"query": {"filtered": {"filter" : {"exists" : {"field" : "unshortened_url"}}}}}}'

echo "--- crawled urls ---"
curl -XPOST localhost:9200/url/unshortened/_count?pretty -d '{"query": {"filtered": {"query": {"bool": {"must_not": {"match": {"crawled_date": "1900-01-01 00:00:00"}}}}, "filter" : {"exists" : {"field" : "crawled_date"}}}}}}'

echo "--- failed urls ---"
curl -XPOST localhost:9200/url/unshortened/_count?pretty -d '{"query": {"match": {"crawled_date": "1900-01-01 00:00:00"}}}'

echo "--- urls waiting ---"
curl -XPOST localhost:9200/url/unshortened/_count?pretty -d '{"query": {"filtered": {"filter" : {"and" : [{"missing" : {"field" : "crawled_date"}}, {"not" : {"term" : {"_duplicated": true}}}]}}}}}'

if [ "$1" = "a" ]
then 
	echo "--- crawled docs ---"
	curl -XPOST forty.tw:18181/tjcl/web/_count?pretty
	echo "--- crawled tweets ---"
	curl -XPOST forty.tw:18181/tjcl/tweet/_count?pretty -d '{"query": {"match": {"_crawled": true}}}'
fi


if [ -f /srv/_tmp/url.tmp ]
then
	if [ -f /srv/_tmp/web.json ]
	then
		echo "--- crawling ---"
		echo $(cat /srv/_tmp/web.json | wc -l) "/"$(cat /srv/_tmp/url.tmp | wc -l)"   crawled"
	else
		echo "--- crawling ---"
		echo "0 /"$(cat /srv/_tmp/url.tmp | wc -l)"   crawled"
	fi
fi