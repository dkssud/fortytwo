#!/bin/bash

ES='http://localhost:9200'
ESIDX='wikipedia'

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

else
  break
fi