#!/bin/bash

ES='http://localhost:9200'
ESIDX='url'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then  
  curl -XPOST $ES/$ESIDX/_close
  curl -XDELETE $ES/$ESIDX

  curl -XPUT $ES/$ESIDX/ -d '{
      "settings": {
          "number_of_shards" :   5,
          "number_of_replicas" : 1
      }
  }'

  curl -XPUT $ES/$ESIDX/unshortened/_mapping -d '{
    "unshortened": {
      "dynamic": true,
      "properties": {
        "original_url": {
          "type": "string"
        },
        "unshortened_url": {
          "type": "string"
        },
        "web_id": {
          "type": "string"
        },
        "text_id": {
          "type": "string"
        },
        "twt_ids": {
          "type": "string"
        },
        "status": {
          "type": "string"
        },
        "crawled_date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"      
        },
        "freq": {
          "type": "long"
        },
        "_duplicated": {
          "type": "boolean"
        },
        "_filtered": {
          "type": "boolean"
        }        
      }
    }
  }'
  
else
  break
fi