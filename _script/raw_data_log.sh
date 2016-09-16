#!/bin/bash
echo "--- raw tweet in ft ---"
curl -XGET forty.tw:18181/*/status/_count?pretty

echo "--- raw tweets in zb ---"
curl -XGET localhost:9200/*/status/_count?pretty

echo "--- raw tumblrs in dk ---"
curl -XGET localhost:9200/dkssud02/text,photo,audio,video,link,quote,chat,answer/_count?pretty

echo "--- raw wikipeda pages in ko ---"
curl -XGET localhost:9200/wikipedia/ko/_count?pretty

echo "--- raw wikipeda pages in en ---"
curl -XGET localhost:9200/wikipedia/en/_count?pretty

echo "--- raw namuwiki pages ---"
curl -XGET localhost:9200/namuwiki/document/_count?pretty