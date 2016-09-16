# -*- coding: utf-8 -*-

import sys
import tweepy
import os
import json

def twitterOauth(userID, CONSUMER_KEY, CONSUMER_SECRET):

    access = []
    with open('/srv/twitter/logstash/input/'+str(userID)+'.oauth') as f:
        for line in f.readlines():
            access.append(line.rstrip())
    ACCESS_TOKEN = access[0]
    ACCESS_TOKEN_SECRET = access[1]

    # auth
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


if __name__ == "__main__":

    # get userID
    f_in = open('/srv/twitter/logstash/input/user.json')
    f_conf = open('/srv/twitter/logstash/twitter.conf', 'w')


    userID_list = []
    dic_consumer_key = {}
    dic_consumer_secret = {}
    dic_token = {}
    dic_secret = {}
    dic_follows = {}

    for line in f_in.readlines():
        user_data = json.loads(line)
        userID = user_data['id']
        consumer_key = user_data['consumer_key']
        consumer_secret = user_data['consumer_secret']

        auth = twitterOauth(userID, consumer_key, consumer_secret)

        token = auth[1]
        secret = auth[2]
        auth = auth[0]

        # Create a tweepy API
        api = tweepy.API(auth_handler = auth, api_root = '/1.1')
    
    
        # Get entire friends_ids of userID
        userlist = []

        userlist = api.friends_ids(userID)
        userlist_str = str(userlist)
        userlist_str = userlist_str.replace("[", "")
        userlist_str = userlist_str.replace("]", "")
        userlist_str = userlist_str.replace(" ", "")
        userlist_str = userlist_str

        userID_list.append(userID)
        dic_consumer_key[userID] = consumer_key
        dic_consumer_secret[userID] = consumer_secret
        dic_token[userID] = token
        dic_secret[userID] = secret
        dic_follows[userID] = userlist_str

    print >> f_conf, "input {"
    for ID in userID_list:
        print >> f_conf, "  twitter {"
        print >> f_conf, "    type => " + "\"" + ID + "\""
        print >> f_conf, "    consumer_key => " + "\"" + dic_consumer_key[ID] + "\""
        print >> f_conf, "    consumer_secret => " + "\"" + dic_consumer_secret[ID] + "\""
        print >> f_conf, "    oauth_token => " + "\"" + dic_token[ID] + "\""
        print >> f_conf, "    oauth_token_secret => " + "\"" + dic_secret[ID] + "\""
        print >> f_conf, "    ids => " + "[" + dic_follows[ID] + "]"
        print >> f_conf, "    full_tweet => true"
        print >> f_conf, "  }"

    print >> f_conf, "}"
    print >> f_conf, "output {"

    for ID in userID_list:
        print >> f_conf, "  if [type] == " + "\"" + ID + "\" {"
        print >> f_conf, "    elasticsearch_http {"
        print >> f_conf, "      host => \"localhost\""
        print >> f_conf, "      index => " + "\"" + ID + "\""
        print >> f_conf, "      index_type => \"status\""
        print >> f_conf, "    }"
        print >> f_conf, "  }"
    print >> f_conf, "}"

        # Convert type of friends_ids to string
        #for i in userlist:
        #    userlist_str.append(str(i))

        #print >> sys.stderr, 'The frineds ids of "%s"' % (userID)
        #print userlist_str, '\n'


