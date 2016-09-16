#!/bin/bash

# declare variables
path=/srv/_tmp
logfile=/srv/_log/crawl.log
error=/srv/_log/crawl_error.log
filter=/srv/_log/crawl_filtered.log
geturl=/srv/_log/get_url.log
trash=/srv/_trash

filename=/srv/twitter/web/chk/crawl.chk

now=$(date +"%Y%m%d-%H%M%S")

# check if file exists or not
if [ -f $filename ]
then
	echo "> started at "$now >> $logfile
	echo "> started at "$now >> $geturl
	mv $filename $trash
else
	echo "------------" >> $logfile
	echo "! no check file matched at "$now >> $logfile
	echo "============" >> $logfile
	exit
fi

# get unshortened urls
python /srv/twitter/web/get_url.py

# check if unshortened urls exit or not
if [ ! -s $path/url.tmp ]
then
	echo "! no url file matched" >> $logfile
	echo "============" >> $logfile
	echo "This file is for checking whether previous process has finished or not." > $filename
	exit
fi

# log: finish geturl, start crawl error, fitler
now=$(date +"%Y%m%d-%H%M%S")
echo "------------" >> $geturl
echo "> finished at "$now >> $geturl
echo "============" >> $geturl
echo "> started at "$now >> $error
echo "------------" >> $error
echo "> started at "$now >> $filter
echo "------------" >> $filter

# log total count of unshortened urls
echo "------------"
echo "------------" >> $logfile
echo "urls before crawl"
echo "urls before crawl" >> $logfile
echo "------------"
echo "------------" >> $logfile
echo $(cat $path/url.tmp | wc -l)" urls"
echo $(cat $path/url.tmp | wc -l)" urls" >> $logfile
cat $path/url.tmp | awk -F'\t' '{s+=$5} END {print s" total count"}'
cat $path/url.tmp | awk -F'\t' '{s+=$5} END {print s" total count"}' >> $logfile


# start crawling
now=$(date +"%Y%m%d-%H%M%S")
echo "------------" >> $logfile
echo "crawl" >> $logfile
echo "------------" >> $logfile
echo "started at "$now >> $logfile

# crawl
cd /srv/twitter/robot
/usr/local/bin/scrapy crawl web_spider
cd /srv/twitter/web

# log time to errors and filtered urls file
now=$(date +"%Y%m%d-%H%M%S")
echo "finished at "$now >> $logfile
echo "------------" >> $error
echo "> finished at "$now >> $error
echo "============" >> $error
echo "------------" >> $filter
echo "> finished at "$now >> $filter
echo "============" >> $filter

# log after crawl
echo "------------"
echo "------------" >> $logfile
echo "docs after crawl"
echo "docs after crawl" >> $logfile
echo "------------"
echo "------------" >> $logfile
echo $(cat $path/spider_url.txt | wc -l)" uniq count"
echo $(cat $path/spider_url.txt | wc -l)" uniq count" >> $logfile
cat $path/spider_url.txt | awk -F'\t' '{s+=$4} END {print s" total count"}'
cat $path/spider_url.txt | awk -F'\t' '{s+=$4} END {print s" total count"}' >> $logfile


# check crawl error and log
python /srv/twitter/web/crawl_check.py
cat $path/crawl_check.tmp | sort | uniq > $path/crawl_check.txt
echo $(cat $path/crawl_check.txt | wc -l)" errors"
echo $(cat $path/crawl_check.txt | wc -l)" errors" >> $logfile
cat $path/crawl_check.txt | awk -F'\t' '{s+=$4} END {print s" total count"}'
cat $path/crawl_check.txt | awk -F'\t' '{s+=$4} END {print s" total count"}' >> $logfile


# trash crawl error log file
mv $path/crawl_check.txt $trash
mv $path/crawl_check.tmp $trash


# index docs
python /srv/twitter/web/index_web.py

# check index error log file
now=$(date +"%Y%m%d-%H%M%S")
echo "------------" >> $logfile
echo "> finished at "$now >> $logfile
echo "============" >> $logfile

mv /srv/_tmp/spider_url.txt $trash
mv /srv/_tmp/url.tmp $trash
mv /srv/_tmp/web.json $trash

echo "This file is for checking whether previous process has finished or not." > $filename



