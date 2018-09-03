from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json , time
import sqlite3
from unidecode import unidecode
from textblob import TextBlob

#Creating DB and Tables to store Stream Data
conn = sqlite3.connect('twitter.db')
c = conn.cursor()
def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))

create_table() 

#Loading Twitter Developer account Credential
with open('config.json', 'r+') as config:
    data = json.load(config)
    API = data['TwitterDetail']['API']
    API_secret = data['TwitterDetail']['API_secret']
    Access = data['TwitterDetail']['Access']
    Access_secret = data['TwitterDetail']['Access_secret']


class listener(StreamListener):
    
    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity
            print(time_ms, tweet, sentiment)
            c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (time_ms, tweet, sentiment))
            conn.commit()
        
        except KeyError as e:
            print(str(e))
        return(True)
    
    def on_error(self, status):
        print (status)

while True:
    try:
        auth = OAuthHandler(API, API_secret)
        auth.set_access_token(Access, Access_secret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=["a","e","i","o","u"])
    except Exception as e:
        print(str(e))
        time.sleep(5)
