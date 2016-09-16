#!/bin/bash

query="에이핑크"

curl -XPOST 'http://forty.tw:18181/tjcl,wiki/_search?pretty' -d '{
  "query": {
    "filtered": {
      "query": {
        "function_score": {
          "query": {
            "multi_match": {
              "query": "'"$query"'",
              "fields": [
                "title^0.7",
                "body",
                "text"
              ],
              "tie_breaker": 0.02,
              "minimum_should_match": "100%"
            }
          },
          "functions": [
            {
              "field_value_factor": {
                "field": "freq",
                "modifier": "log1p",
                "factor": 2
              }
            },
            {
              "weight": 5,
              "exp": {
                "date": {
                  "scale": "5d",
                  "decay": 0.7
                }
              }
            }
          ],
          "boost_mode": "sum",
          "score_mode": "sum"
        }
      },
      "filter": {
        "and": [{
          "bool": {
            "must_not": {
              "term": {
                "_filtered": true
              }
            }
          }
        },
        {
          "bool": {
            "must_not": {
              "term": {
                "_crawled": true
              }
            }
          }
        }]
      }      
    }
  }
}'