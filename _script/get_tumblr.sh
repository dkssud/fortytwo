#!/bin/bash
if [ "$1" = "d" ]
then
	index_name="dkssud02"
else
	exit
fi

echo "--- raw tumblr posts in zb ---"
curl -XGET localhost:9200/$index_name/text,photo,audio,video,link,quote,chat,answer/_count?pretty

echo "--- text ---"
curl -XGET localhost:9200/$index_name/text/_count?pretty

echo "--- photo ---"
curl -XGET localhost:9200/$index_name/photo/_count?pretty

echo "--- audio & video ---"
curl -XGET localhost:9200/$index_name/audio,video/_count?pretty

echo "--- etc ---"
curl -XGET localhost:9200/$index_name/link,quote,chat,answer/_count?pretty