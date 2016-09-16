#!/bin/bash
now=$(date +"%Y%m%d")

mv /srv/_log/crawl.log /srv/_log/_previous/crawl_$now.log
mv /srv/_log/crawl_error.log /srv/_log/_previous/crawl_error_$now.log
mv /srv/_log/crawl_filtered.log /srv/_log/_previous/crawl_filtered_$now.log
mv /srv/_log/get_url.log /srv/_log/_previous/get_url_$now.log