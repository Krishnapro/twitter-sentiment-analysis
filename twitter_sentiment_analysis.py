import logging

import tweepy
import pandas as pd
import sys

import pickle
import csv

from nltk.inference.mace import arguments
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import wordnet
import secrets

# if sys.version_info[0] < 3:
#     input = raw_input


# authenticating with authentication variables
consumer_key = 'G3vGhOTy8oJ8v0RqpCu7F9CVP'
consumer_Secret = 'o4LEerI04y5TH6ZzH9FdRoe2mfpFPmKyaZCJZZQTmoOHIQhwCy'
access_Token = '911084322274213888-fjcAayIA3nYVD1cEpLkXyZi7wKA7Ak4'
access_Token_Secret = 'g0Vmw26RLWWOQuxrsyDKbMWLToLvwjqrN1CbFDBPN2J5W'

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_Secret)
auth.set_access_token(access_Token, access_Token_Secret)
api = tweepy.API(auth)

# Error handling
if (not api):
    print("Problem connecting to API")

hash_tag = input("Please enter keyword or hashtag to search: ")
number = int(input("Please enter how many tweet to analyse: "))
# location = input("What is the location of party? \n")

# Gettting geo id for places
# places = api.geo_search(query=location)

# place id
# print(places[10])

tweetsPerQry = 1000  # this is the max the api permits

# if results from a specific id onwards are reqd, set since_id to that ID.
# else default to no lower limit , go as far back as API allows
sinceId = None

max_id = -1
data = None

dataset = []
outputFile = 'test.data'
fw = open(outputFile, 'wb')

tweetCount = 0
print("Downloading max{0} tweets".format(number))
while tweetCount < number:
    try:
        if max_id <= 0:
            if not sinceId:
                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry, tweet_mode='extended', lang='en')
                tweetCount += len(new_tweets)
                print("Download {0} tweets".format(tweetCount))
            else:
                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended',
                                        lang='en')
                print("here 2")
        else:
            if (not sinceId):
                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry, max_id=str(max_id - 1), tweets_mode='extended',
                                        lang='en')
                print("here 3")
            else:
                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId,
                                        tweet_mode='extended', lang='en')
                print("here 4")
            if not new_tweets:
                print("No more tweets found")
                break

        # print(new_tweets)

        tweets = new_tweets
        for tweet in tweets:
            dataset.append(tweet.full_text)
        tweetCount += len(new_tweets)
        print("Download {0} tweets".format(tweetCount))
        max_id = new_tweets[-1].id


    except tweepy.TweepyException as e:
        print(str(e))
        break
pickle.dump(dataset, fw)
fw.close()

inputFile = 'test.data'
fd = open(inputFile, 'rb')
dataset = pickle.load(fd)
print(dataset)


#sentiment analysis
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

l = []
counter = Counter()

for data in dataset:
    ss = sid.polarity_scores(data)  #polarity score is calculated
    l.append(ss)
    k = ss['compound']
    if k >= 0.05:
        counter['positive'] += 1
    elif k < -0.05:
        counter['negative'] += 1
    else:
        counter['neutral'] += 1

positive = counter['positive']
negative = counter['negative']
neutral = counter['neutral']



labels = ['Positive [' + str(positive) + '%]', 'Negative [' + str(negative) + '%]', 'Neutral [' + str(neutral) + '%]']
sizes = [positive, negative, neutral]
colors = ['green', 'red', 'grey']
# use matplotlib to the chart
plt.pie(
    sizes,
    colors=colors,
    # shadow=True,
    # labels=labels,
    startangle=90,
    autopct='%.0f%%'
)
plt.style.use('default')
plt.legend(labels)
plt.title("Sentiment Analysis Result for keyword=  "+hash_tag+"\n\n")
plt.axis('equal')

plt.title("Sentiment of {} Tweets about {}".format(number, hash_tag))
plt.show()

