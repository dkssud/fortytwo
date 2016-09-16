#!/bin/bash

if [ "$1" = "t" ]
then
	cluster_name="forty.tw:18181"
	index_name="tjcl"
	type_name="tweet"
elif [ "$1" = "w" ]
then
	cluster_name="forty.tw:18181"
	index_name="tjcl"
	type_name="web"
elif [ "$1" = "u" ]
then
	cluster_name="localhost:9200"
	index_name="url"
	type_name="unshortened"
else
	exit
fi

echo "--- total docs ---"
curl -XGET $cluster_name/$index_name/$type_name/_count?pretty

echo "--- checked ---"
curl -XPOST $cluster_name/$index_name/$type_name/_count?pretty -d '{"query": {"filtered": {"filter": {"exists": {"field": "text_id"}}}}}}'

echo "--- filtered ---"
curl -XPOST $cluster_name/$index_name/$type_name/_count?pretty -d '{"query": {"match": {"_filtered": true}}}'

if [ "$2" = "a" ]
then
	echo "--- no text ---"
	curl -XPOST $cluster_name/$index_name/$type_name/_count?pretty -d '{"query": {"match": {"text_id": "no text"}}}'

	echo "--- duplicated ---"
	curl -XPOST $cluster_name/$index_name/$type_name/_count?pretty -d '{"query": {"match": {"_duplicated": true}}}'
fi

echo "--- waiting ---"
curl -XPOST $cluster_name/$index_name/$type_name/_count?pretty -d '{"query": {"filtered": {"filter": {"missing": {"field": "text_id"}}}}}'