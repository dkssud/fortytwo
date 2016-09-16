#!/bin/bash

ES='http:/forty.tw:18181'
ESIDX='tjcl'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then
  curl -XDELETE $ES/$ESIDX/tweet

  curl -XPUT $ES/$ESIDX/tweet/_mapping -d '{
    "tweet": {
      "dynamic": true,
      "properties": {
        "twt_id": {
          "type": "string"
        },
        "idx_from": {
          "type": "string"
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
        "date_local": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "rt_count": {
          "type": "long"
        },
        "fav_count": {
          "type": "long"
        },
        "freq": {
          "type": "long"
        },
        "user_id": {
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
        "user_screen_name": {
          "type": "string",
          "index": "analyzed",
          "index_options": "docs",
          "norms": {
            "enabled": false
          }
        },
        "user_image": {
          "type": "string"
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
        "display_urls": {
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
        "hashtags": {
          "type": "string"
        },
        "mentions": {
          "type": "string"
        },
        "reply_to_id": {
          "type": "string"
        },
        "sensitive": {
          "type": "boolean"
        },
        "_updated": {
          "type": "boolean"
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
