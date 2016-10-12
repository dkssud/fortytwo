#!/bin/bash

ES='http://localhost:9200'
ESIDX='fortytwo'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then
  curl -XPOST $ES/$ESIDX/_close
  curl -XDELETE $ES/$ESIDX

  curl -XPUT $ES/$ESIDX/ -d '{
    "settings": {
      "index": {
        "analysis": {
          "analyzer": {
            "korean_index": {
              "type": "custom",
              "tokenizer": "mecab_ko_standard_tokenizer"
            },
            "korean_query": {
              "type": "custom",
              "tokenizer": "korean_query_tokenizer"
            }
          },
          "tokenizer": {
            "korean_query_tokenizer": {
              "type": "mecab_ko_standard_tokenizer",
              "compound_noun_min_length": 100
            }
          }
        }
      }
    }
  }'

  curl -XPOST $ES/$ESIDX/_open

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
