import twitter
import xhtml2pdf.pisa as pisa

from jinja2 import Environment, PackageLoader

from settings import *


jinja_env = Environment(loader=PackageLoader(__name__, 'templates'))


def get_tweets(user):
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)

    last_max_id = None
    result = []

    # Get the tweets!
    for _ in range(ITERATE_TIMES):
        tweets = api.GetUserTimeline(
            screen_name=user, count=200, include_rts=False, max_id=last_max_id
        )

        for tweet in tweets:
            caps_letters = sum(1 for c in tweet.text if c.isupper())
            newlines = sum(1 for c in tweet.text if c == '\n')
            reply_to = tweet.in_reply_to_screen_name

            if caps_letters > 20 and newlines > 2:
                tweet_text = tweet.text

                # remove replies
                if reply_to is not None:
                    tweet_text = tweet_text[3 + len(reply_to):]

                # remove urls at the end of the tweet
                if tweet.urls:
                    offset = len(tweet_text) - sum(len(url.url) for url in tweet.urls) - 3
                    tweet_text = tweet_text[:offset]

                result.append({
                    'created_at': tweet.created_at,
                    'text': tweet_text,
                })

        last_max_id = tweets[-1].id

    return result


def generate_pdf(filename, username='', tweets=None):
    if tweets is None:
        tweets = []

    template = jinja_env.get_template('pdf_template.html')

    for tweet in tweets:
        tweet['text'] = tweet['text'].replace('\n', '<br>')

    html = template.render(username=username, tweets=tweets, font_path=FONT_PATH)
    html = html.encode("UTF-8")

    with open(filename, "w+b") as file_obj:
        pisa.CreatePDF(html, file_obj, encoding='UTF-8')


if __name__ == '__main__':
    tweets = get_tweets(TWITTER_USERNAME)
    generate_pdf('tweets.pdf', TWITTER_USERNAME, tweets)
