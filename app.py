from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import Markup
import os

from matplotlib import pyplot as plt
from matplotlib.pyplot import legend
from nltk.corpus import wordnet

from twitter_sentiment_analysis import consumer_key, consumer_Secret, access_Token, access_Token_Secret, hash_tag, \
    number, sizes, colors, labels

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'o4LEerI04y5TH6ZzH9FdRoe2mfpFPmKyaZCJZZQTmoOHIQhwCy'
#session.init_app(app)

positive = 0
negative = 0
neutral = 0


@app.route('/')
def home():
    if not session.get('searched'):
        return render_template('search.html')
    else:
        labels = ["Positive", "Negative", "Neutral"]

        global positive
        global negative
        global neutral
        # labels = ['Positive [' + str(positive) + '%]', 'Negative [' + str(negative) + '%]',
        #           'Neutral [' + str(neutral) + '%]']

        values = [positive, negative, neutral]
        colors = ['green', 'red', 'grey']

        session['searched'] = False
        return render_template('chart.html', set=zip(values, labels, colors))


@app.route('/search', methods=['POST'])
def do_search():
    if request.form['search_query'] == '':
        flash('Search Queary cannot be empty!')
        session['searched'] = False
    if request.form['max_tweets'] == '':
        flash('Max Tweets cannot be empty!')
        session['searched'] = False
    else:
        if not request.form['max_tweets'].isdigit():
            flash('Max Tweets should be a number!')
            session['searched'] = False
        else:
            if int(request.form['max_tweets']) > 0 & int(request.form['max_tweets']) <= 100000:
                import tweepy
                import sys
                import csv
                import pickle
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                from collections import Counter

                # importing the auth variables from secret.py

                # authenicating with authentication variables
                auth = tweepy.OAuth1UserHandler(consumer_key, consumer_Secret)
                auth.set_access_token(access_Token, access_Token_Secret)
                api = tweepy.API(auth)
                # Error handling
                if (not api):
                    print("Problem Connecting to API")

                # inputs for counts taken
                hash_tag = request.form['search_query']
                number = int(request.form['max_tweets'])
                # location = input("What is the location of party? \n")


                tweetsPerQry = 1000  # this is the max the API permits

                # If results from a specific ID onwards are reqd, set since_id to that ID.
                # else default to no lower limit, go as far back as API allows
                sinceId = None

                # If results only below a specific ID are, set max_id to that ID.
                # else default to no upper limit, start from the most recent tweet matching the search query.
                max_id = -1
                data = None

                dataset = []
                outputFile = 'test.data'
                fw = open(outputFile, 'wb')

                tweetCount = 0
                print("Downloading max {0} tweets".format(number))
                while tweetCount < number:
                    try:
                        if (max_id <= 0):
                            if (not sinceId):
                                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry, tweet_mode='extended', lang='en')
                                tweetCount += len(new_tweets)
                                print("Downloaded {0} tweets".format(tweetCount))
                            else:
                                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry,
                                                        since_id=sinceId, tweet_mode='extended', lang='en')
                                print("here 2")
                        else:
                            if (not sinceId):
                                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry,
                                                        max_id=str(max_id - 1), tweet_mode='extended', lang='en')
                                print("here 3")
                            else:
                                new_tweets = api.search_tweets(q=hash_tag, count=tweetsPerQry,
                                                        max_id=str(max_id - 1),
                                                        since_id=sinceId, tweet_mode='extended', lang='en')
                                print("here 4")
                            if not new_tweets:
                                print("No more tweets found")
                                break

                        # print(new_tweets)

                        tweets = new_tweets
                        for tweet in tweets:
                            dataset.append(tweet.full_text)
                        #data += pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
                        tweetCount += len(new_tweets)
                        print("Downloaded {0} tweets".format(tweetCount))
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


                import nltk
                nltk.download('stopwords')

                sid = SentimentIntensityAnalyzer()

                l = []
                counter = Counter()

                for data in dataset:
                    ss = sid.polarity_scores(data)
                    l.append(ss)
                    k = ss['compound']
                    if k >= 0.05:
                        counter['positive'] += 1
                    elif k <= -0.05:
                        counter['negative'] += 1
                    else:
                        counter['neutral'] += 1

                global positive
                positive = counter['positive']
                global negative
                negative = counter['negative']
                global neutral
                neutral = counter['neutral']

                session['searched'] = True

    return home()


app.secret_key = 'abcdefghi'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)