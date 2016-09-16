#!/bin/bash
echo "--- tweet ---"
curl -XGET forty.tw:18181/tjcl/tweet/_count?pretty

if [ "$1" = "a" ]
then
	echo "--- url ---"
	curl -XGET localhost:9200/url/unshortened/_count?pretty
fi

echo "--- web ---"
curl -XGET forty.tw:18181/tjcl/web/_count?pretty

echo "--- tumblr ---"
curl -XGET forty.tw:18181/tjcl/tumblr/_count?pretty

echo "--- wikipedia ko ---"
curl -XGET forty.tw:18181/wiki/wikipediako/_count?pretty

echo "--- wikipedia en ---"
curl -XGET forty.tw:18181/wiki/wikipediaen/_count?pretty

echo "--- namuwiki ---"
curl -XGET forty.tw:18181/wiki/namuwiki/_count?pretty