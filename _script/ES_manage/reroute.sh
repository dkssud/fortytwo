curl -XPOST 'http://localhost:9200/_cluster/reroute' -d '{
    "commands": [{
        "allocate": {
            "index": "44526785",
            "shard": 2,
            "node": "JB1PrrqlRsGSEBIK7gqt0A",
            "allow_primary": true
        }
    }]
}'
