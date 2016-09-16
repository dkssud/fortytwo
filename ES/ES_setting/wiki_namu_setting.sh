#!/bin/bash

ES='http://forty.tw:18181'
ESIDX='wiki'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then
  curl -XDELETE $ES/$ESIDX/namuwiki

  curl -XPUT $ES/$ESIDX/namuwiki/_mapping -d '{
    "namuwiki": {
      "dynamic": true,
      "properties": {
        "wiki_id": {
          "type": "string"
        },
        "title": {
          "type": "string",
          "index": "analyzed",
          "index_analyzer": "korean_index",
          "search_analyzer": "korean_query",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "wiki_body": {
          "type": "string",
          "index": "analyzed",
          "index_analyzer": "korean_index",
          "search_analyzer": "korean_query"
        },
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "date_timestamp": {
          "type": "integer"
        },
        "freq": {
          "type": "long"
        },
        "domain": {
          "type": "string",
          "index": "analyzed",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "original_urls": {
          "type": "string"
        },
        "target_urls": {
          "type": "string"
        },
        "img_urls": {
          "type": "string"
        },
        "original_img_urls": {
          "type": "string"
        },
        "cached_img_urls": {
          "type": "string"
        },
        "width": {
          "type": "string"
        },
        "_duplicated": {
          "type": "boolean"
        },
        "_filtered": {
          "type": "boolean"
        },
        "_img_cached": {
          "type": "boolean"
        }
      }
    }
  }'


else
  break
fi