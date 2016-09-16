#!/bin/bash

# declare variables
filename=/srv/tumblr/index_tumblr/chk/idxtumblr.chk
now=$(date +"%Y%m%d-%H%M%S")

# check if file exists or not
if [ -f "$filename" ]
then
	echo "> started at "$now
	echo "tumblrs from "$1
	echo "tumblr type: "$2
	echo "------------"
	mv $filename /srv/_trash
else
	echo "------------"
	echo "! no check file matched at "$now
	echo "============"
	exit
fi


# run unshorten
python /srv/tumblr/index_tumblr/index_tumblr.py $1 $2

# make finish-check file
now=$(date +"%Y%m%d-%H%M%S")

echo "------------"
echo "> finished at "$now
echo "============"
echo "This file is for checking whether previous process has finished or not." > $filename

