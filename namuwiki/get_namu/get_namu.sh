#!/bin/bash

# declare variables
now=$(date +"%Y%m%d-%H%M%S")

# log start
echo "> started at "$now
echo "namuwiki"
echo "------------"

# run get_namu.py
python /srv/namuwiki/get_namu/get_namu.py

# make finish-check file
now=$(date +"%Y%m%d-%H%M%S")

echo "------------"
echo "> finished at "$now
echo "============"

