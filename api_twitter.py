import tweepy as tw
import datetime


API_KEY = "1xI3KBCyJOI2XhxGEYYw8gcNv"
API_SECRET = "nh938oEgYe8cltrjRkZS6LMgRDcuNykIkB7PGOgxglQm0W9fXm"
TOKEN = "477077516-YdBHbfCFenmOSoblT318HLuvipAvrshktOeOYpNw"
SECRET_TOKEN = "I6dFevJUDzR6AwYuorbdNrpKVjCc3M2NJFTGVwTStYtE0"

auth = tw.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(TOKEN, SECRET_TOKEN)
api = tw.API(auth, wait_on_rate_limit=True)


def get_tweets(keyword):
    """
    Return a list of the 50 last tweets matching a keyword
    :param keyword: The keyword for tweets search
    :return: a list of tweets
    """
    tweets = []
    keyword = str(keyword)
    for tweet in tw.Cursor(api.search, q=keyword, lang="en").items(50):
        tweets.append(tweet)
    return tweets


def time_laps(tweets):
    """
    Get time difference between more last and first tweet within a tweets list. If the list is large enough, the smaller
    the result the more frequent are the tweets within the list. Can allow to measure popularity if all tweets are based
    on the same subject.
    :param tweets: a list of tweets
    :return: the time difference in seconds
    """
    try:
        time_delta = tweets[0].created_at - tweets[len(tweets) - 1].created_at
        return time_delta.total_seconds()
    except Exception:
        return -1


POSITIVE_WORDS = ['good', 'great', 'best', 'excellent', 'fun', 'funny', 'nice', 'love', 'amazing', 'cool', 'fantastic',
                  'fabulous', 'happy', 'nice', 'awesome', 'beautiful', 'perfect', 'terrific', 'phenomenal', 'brilliant',
                  'delight', 'ecstatic', 'elegant', 'exciting', 'genius', 'intelligent', 'intuitive', 'inventive',
                  'creative', 'lovely', 'marvelous', 'one-hundred', 'pleasant', 'positive', 'powerful', 'pretty',
                  'remarkable', 'right', 'success', 'superb', 'secure', 'stunning', 'special', 'outstanding', 'wow',
                  'wonderful', 'fair']
NEGATIVE_WORDS = ['bad', 'worse', 'worst', 'boring', 'shit', 'garbage', 'hate', 'awful', 'trash', 'incompetent',
                  'sad', 'terrible', 'horrible', 'mediocre', 'bullshit', 'crap', 'wrong', 'abysmal', 'atrocious',
                  'collapse', 'bug', "can't", 'deplorable', 'disgusting', "don't", 'fail', 'filthy', 'gross', 'hard',
                  'hideous', 'insipid', 'inelegant', 'injurious', 'imperfect', 'lousy', 'messy', 'missing', 'offensive',
                  'oppressive', 'poor', 'questionable', 'quit', 'stupid', 'stressful', 'unwelcome', 'unwanted',
                  'unsatisfactory', 'unhappy', 'unwise', 'unfair', 'unpleasant', 'worthless', 'zero']


def tweet_score(tweet):
    """
    Get a score to determine if a tweet is positive or negative based on keywords.
    :param tweet: a tweet
    :return: the tweet score
    """
    score = 0
    for word in POSITIVE_WORDS:
        if word in tweet.text.lower():
            score += 1
    for word in NEGATIVE_WORDS:
        if word in tweet.text.lower():
            score -= 1
    return score


def scores_sum(tweets):
    """
    Get the sum of tweet scores within a list of tweets
    :param tweets: a list of tweets
    :return: the cumulative score
    """
    total_score = 0
    for t in tweets:
        total_score += tweet_score(t)
    return total_score
