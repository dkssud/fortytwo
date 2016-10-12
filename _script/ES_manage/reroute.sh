curl -XPOST 'http://localhost:9200/_cluster/reroute' -d '{
    "commands": [{
        "allocate": {
            "index": "_river",
            "shard": 0,
            "node": "T3AcO-ajRJuCOyTL6GsjEQ",
            "allow_primary": true
        }
    }]
}'
