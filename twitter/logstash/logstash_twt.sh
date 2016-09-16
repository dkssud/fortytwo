#!/bin/bash

# get follow ids of user
python logstash_twt.py

# start logstash
launchctl load /Users/dkssud/Library/LaunchAgents/homebrew.mxcl.logstash-twitter.plist
#logstash agent -f twitter.conf