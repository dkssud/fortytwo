#!/bin/bash

# declare variables
filename=/srv/twitter/twt/chk/idxtwt.chk
now=$(date +"%Y%m%d-%H%M%S")

# check if file exists or not
if [ -f "$filename" ]
then
	echo "> started at "$now
	echo "tweets from "$1
	echo "------------"
	mv $filename /srv/_trash
else
	echo "------------"
	echo "! no check file matched at "$now
	echo "============"
	exit
fi


# run index_twt python file
python /srv/twitter/twt/index_twt.py $1

# make finish-check file
now=$(date +"%Y%m%d-%H%M%S")
echo "------------"
echo "> finished at "$now
echo "============"
echo "This file is for checking whether previous process has finished or not." > $filename

