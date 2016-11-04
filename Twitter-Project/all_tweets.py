import tweepy
import psycopg2

#Twitter API credentials
consumer_key = '' #substitute values from twitter website
consumer_secret = ''
access_key = ''
access_secret = ''


def get_all_tweets(screen_names):
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	for screen_name in screen_names:
		alltweets = []
		#make initial request for most recent tweets (200 is the maximum allowed count)
		new_tweets = api.user_timeline(screen_name = screen_name,count=200)
		#save most recent tweets
		alltweets.extend(new_tweets)

		#save the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

		#keep grabbing tweets until there are no tweets left to grab

		while len(new_tweets) > 0:
			print "getting tweets before %s" % (oldest)

			#all subsiquent requests use the max_id param to prevent duplicates
			new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

			#save most recent tweets
			alltweets.extend(new_tweets)

			#update the id of the oldest tweet less one
			oldest = alltweets[-1].id - 1

			print "...%s tweets downloaded so far" % (len(alltweets))



		#transform the tweets into 2D array to be inserted to postgresql
		outtweets = [[screen_name, tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.favorite_count, tweet.retweet_count] for tweet in alltweets]

		#write the table
		insert_table(outtweets)

def insert_table(tweets):
    """ insert to the PostgreSQL database"""
    sql = (
        """
		INSERT INTO company_tweets(Company,id,created_at,tweet,favorite_count,retweet_count)
             VALUES(%s, %s, %s, %s, %s, %s);
		""")
    conn = None

    try:
        # read the connection parameters
        conn = psycopg2.connect("dbname=twitter user=postgres password=password")
        cur = conn.cursor()
        # add all tweets to the table
        cur.executemany(sql, tweets)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
	#pass in the usernames of the account you want to download
	users = int(raw_input("Enter number of users: "))
	screen_names=[]
	for user in range(users):
		screen_names.append(raw_input("Enter Screen Name: "))
	get_all_tweets(screen_names)
