#!/bin/bash

ES='http://forty.tw:18181'
ESIDX='tjcl'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then 
  curl -XDELETE $ES/$ESIDX/web

  curl -XPUT $ES/$ESIDX/web/_mapping -d '{
    "web": {
      "dynamic": true,
      "properties": {
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
        "body": {
          "type": "string",
          "index": "analyzed",
          "index_analyzer": "korean_index",
          "search_analyzer": "korean_query"
        },
        "text": {
          "type": "string",
          "index": "analyzed",
          "index_analyzer": "korean_index",
          "search_analyzer": "korean_query",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "text_display": {
          "type": "string"
        },
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "date_timestamp": {
          "type": "long"
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
        "domain_url": {
          "type": "string"
        },
        "user_name": {
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
        "unshortened_urls": {
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
        "body_rule": {
          "type": "string",
          "index": "analyzed",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "date_rule": {
          "type": "string",
          "index": "analyzed",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "crawled_date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "text_id": {
          "type": "string"
        },
        "web_id": {
          "type": "string"
        },
        "twt_ids": {
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