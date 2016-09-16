#!/bin/bash
now=$(date +"%Y%m%d")

mv /srv/_log/index_twt.log /srv/_log/_previous/index_twt_$now.log
mv /srv/_log/get_tumblr.log /srv/_log/_previous/get_tumblr_$now.log
mv /srv/_log/index_tumblr.log /srv/_log/_previous/index_tumblr_$now.log
mv /srv/_log/index_wiki.log /srv/_log/_previous/index_wiki_$now.log
mv /srv/_log/get_namuwiki.log /srv/_log/_previous/get_namuwiki_$now.log
mv /srv/_log/index_namuwiki.log /srv/_log/_previous/index_namuwiki_$now.log