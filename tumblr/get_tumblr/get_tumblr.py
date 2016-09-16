# -*- coding: utf-8 -*-

import json
import elasticq
import pytumblr
import time

# utf-8 encoding
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == "__main__":


    # Authenticate via OAuth
    client = pytumblr.TumblrRestClient(
        'Pnf1xSey398BluTP9EUdLeCFd0UjiZ8nbAu892fXnj56gFukit',
        '5acVQwrVk36pBz5RRFCxEEzlUEUf5UGLwN1ztu12SwRnYMFOs8',
        'KZEOmlziAuHg4p44JQ0DryaQQEqbPc3nwnqojw9f7aX29Rde0q',
        'YzSCXfysu0xauhObX5oyuXGzqgFYLf9CLIZLWUSiUH9BN5DwSR'
        )

    # Authenticate without OAuth
    client_wo_oauth = pytumblr.TumblrRestClient(
        'Pnf1xSey398BluTP9EUdLeCFd0UjiZ8nbAu892fXnj56gFukit',
        '5acVQwrVk36pBz5RRFCxEEzlUEUf5UGLwN1ztu12SwRnYMFOs8',
        )

    # initialize vars
    counter = 0
    result_count = 1
    url = None
    url_list = ['dkssud02.tumblr.com']

    # get-posts loop
    while (counter < result_count):

        # initialize vars
        following = {}
        users = {}

        # get following list
        following = client.following(offset=counter)
        result_count = following['total_blogs']
        blogs = following['blogs']

        # increase counter
        counter += 20

        for blog in blogs:
            # get blog url
            url = blog['url']
            # process blog url
            url_stripped = None
            url_stripped = str(url)
            url_stripped = url_stripped.replace('http://', '')
            url_stripped = url_stripped.rstrip('/')

            # make url_list
            if url_stripped != None:
                if url_stripped not in url_list:
                    url_list.append(url_stripped)

    
    #print url_list
    #print len(url_list)

    # initialize counter vars for log
    counter_insert = 0
    counter_update = 0
    counter_post = 0
    counter_error = 0


    for url in url_list:

        #initialize vars
        counter = 0
        result_count = 1
        counter_update_tmp = 0

        #print 'start url:', url

        # index loop
        while (counter < result_count):

            # get posts from start url
            posts = {}
            posts = client_wo_oauth.posts(url, offset=counter, limit=20, filter='text')
            
            # check whether post exists or not
            key = 'total_posts'
            if key in posts:
                result_count = posts['total_posts']
                posts = posts['posts']
            else:
                #print 'no docs'
                break
            
            # increase counter
            counter += 20


            for post in posts:

                # count and initialize vars
                counter_post += 1
                post_id = None
                post_type = None
                post_trail = {}

                # get post id and post type
                post_id = post['id']
                post_type = post['type']

                # for time calculation
                #timestamp = 0
                #timegap = 0
                #timestamp = post['timestamp']
                #now = int(time.time())
                #timegap = now - timestamp
                #if gap < 259200:

                # delete 'blog' to avoid indexing error (multiple types found in 'header_bounds')
                key = 'trail'
                if key in post:
                    post_trail = post[key]
                    if len(post_trail) > 0:
                        i = 0
                        while (i < len(post_trail)):
                            del post['trail'][i]['blog']
                            i += 1


                # index
                if post_id != None and post_type != None:
                    update_result = elasticq.putQ('localhost:9200', 'dkssud02', str(post_type), str(post_id), json.dumps(post))

                # check error
                key = 'error'
                if key not in update_result:

                    # check updated or inserted
                    if update_result['_version'] == 1:
                        counter_insert += 1
                    else:
                        counter_update += 1
                        counter_update_tmp += 1

                        # only process recent 10 previously-indexed-docs
                        if counter_update_tmp < 10:
                            pass
                        else:
                            counter = result_count
                            break

                # log error
                else:
                    counter_error += 1
                    print "! error occurred while indexing tumblr"
                    print 'error:', post_id
                    print update_result
                    print post

            #print counter_update_tmp                

    # log 'no error'
    if counter_error == 0:
        print "> no error"            
            

    # log after finish indexing
    print "------------"
    print "after indexing tumblr"
    print "------------"
    print counter_insert, "posts inserted"
    print counter_update, "posts updated"
    print counter_error, "errors"
    #sys.exit(0)





