#!/bin/bash

ES='http://210.106.62.110:18181'
ESIDX='suggest'

echo "password?"
read password

if [ $password == 'tuxmftm' ]
then

  curl -XDELETE $ES/$ESIDX/completion

  curl -XPUT $ES/$ESIDX/completion/_mapping -d '{
    "completion" : {
      "properties" : {
        "keyword" : { "type" : "string" },
          "suggest" : { "type" : "completion",
            "index_analyzer" : "simple",
            "search_analyzer" : "simple",
            "payloads" : true,
            "preserve_separators" : true
          }
        }
      }
    }
  }'

else
  break
fi
