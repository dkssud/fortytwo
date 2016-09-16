#!/bin/bash

# select cluster_name
if [ "$1" = "f" ]
then
	cluster_name="forty.tw:18181"
elif [ "$1" = "z" ] || [ "$1" = "d" ]
then
	cluster_name="localhost:9200"
elif [ "$1" = "wk" ]
then
	cluster_name="localhost:9200"
	type_name="ko"
elif [ "$1" = "we" ]
then
	cluster_name="localhost:9200"
	type_name="en"
elif [ "$1" = "nm" ]
then
	cluster_name="localhost:9200"
	type_name="document"
else
	exit
fi

# count tweet index
if [ "$1" = "f" ] || [ "$1" = "z" ]
then
	echo "--- total status ---"
	curl -XGET $cluster_name/*/status/_count?pretty

	echo "--- indexed ---"
	curl -XPOST $cluster_name/*/status/_count?pretty -d '{"query": {"match": {"_indexed": true}}}'

	echo "--- waiting ---"
	curl -XPOST $cluster_name/*/status/_count?pretty -d '{"query": {"bool": {"must_not": {"match": {"_indexed": true}}}}}'

	if [ "$2" = "a" ]
	then 
		echo "--- uniq tweets indexed ---"
		curl -XGET forty.tw:18181/tjcl/tweet/_count?pretty
	fi

fi

# count tumblr index
if [ "$1" = "d" ]
then
	echo "--- total tumblr posts ---"
	curl -XGET $cluster_name/*/text,photo,audio,video,link,quote,chat,answer/_count?pretty

	echo "--- indexed ---"
	curl -XPOST $cluster_name/*/text,photo,audio,video,link,quote,chat,answer/_count?pretty -d '{"query": {"match": {"_indexed": true}}}'

	echo "--- waiting ---"
	curl -XPOST $cluster_name/*/text,photo,audio,video,link,quote,chat,answer/_count?pretty -d '{"query": {"bool": {"must_not": {"match": {"_indexed": true}}}}}'

	if [ "$2" = "a" ]
	then 
		echo "--- uniq tumblr posts indexed ---"
		curl -XGET forty.tw:18181/tjcl/tumblr/_count?pretty
	fi
fi

# count wikipedia index
if [ "$1" = "wk" ] || [ "$1" = "we" ]
then
	echo "--- total wikipedia pages ---"
	curl -XGET $cluster_name/wikipedia/$type_name/_count?pretty

	echo "--- indexed ---"
	curl -XPOST $cluster_name/wikipedia/$type_name/_count?pretty -d '{"query": {"match": {"_indexed": true}}}'

	echo "--- waiting ---"
	curl -XPOST $cluster_name/wikipedia/$type_name/_count?pretty -d '{"query": {"bool": {"must_not": {"match": {"_indexed": true}}}}}'

	if [ "$2" = "a" ]
	then 
		echo "--- uniq wikipedia pages indexed ---"
		if [ "$1" = "wk" ]
		then
			curl -XGET forty.tw:18181/wiki/wikipediako/_count?pretty
		elif [ "$1" = "we" ]
		then
			curl -XGET forty.tw:18181/wiki/wikipediaen/_count?pretty
		fi
	fi
fi

# count namuwiki index
if [ "$1" = "nm" ]
then
	echo "--- total namuwiki pages ---"
	curl -XGET $cluster_name/namuwiki/$type_name/_count?pretty

	echo "--- indexed ---"
	curl -XPOST $cluster_name/namuwiki/$type_name/_count?pretty -d '{"query": {"match": {"_indexed": true}}}'

	echo "--- waiting ---"
	curl -XPOST $cluster_name/namuwiki/$type_name/_count?pretty -d '{"query": {"bool": {"must_not": {"match": {"_indexed": true}}}}}'

	if [ "$2" = "a" ]
	then 
		echo "--- uniq namuwiki pages indexed ---"
		curl -XGET forty.tw:18181/wiki/namuwiki/_count?pretty
	fi
fi


