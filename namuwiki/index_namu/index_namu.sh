#!/bin/bash

# declare variables
filename=/srv/wikipedia/index_wiki/chk/idxwiki.chk
now=$(date +"%Y%m%d-%H%M%S")

# check if file exists or not
if [ -f "$filename" ]
then
	echo "> started at "$now
	echo "------------"
	mv $filename /srv/_trash
else
	echo "------------"
	echo "! no check file matched at "$now
	echo "============"
	exit
fi


# run unshorten
python /srv/namuwiki/index_namu/index_namu.py

# make finish-check file
now=$(date +"%Y%m%d-%H%M%S")

echo "------------"
echo "> finished at "$now
echo "============"
echo "This file is for checking whether previous process has finished or not." > $filename

