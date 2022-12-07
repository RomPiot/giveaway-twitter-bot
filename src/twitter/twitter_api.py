import tweepy

import config


class TwitterApi:
    def __init__(self):
        self.client = self.get_twitter_client()
        self.api = self.get_twitter_api()

    @staticmethod
    def get_twitter_api():
        auth = tweepy.OAuth2AppHandler(
            consumer_key=config.twitter_credentials["client_id"],
            consumer_secret=config.twitter_credentials["client_secret"]
        )

        return tweepy.API(auth, wait_on_rate_limit=True)

    @staticmethod
    def get_twitter_client():
        return tweepy.Client(
            consumer_key=config.twitter_credentials["client_id"],
            consumer_secret=config.twitter_credentials["client_secret"],
            bearer_token=config.twitter_credentials["bearer_token"],
            access_token=config.twitter_credentials["access_token"],
            access_token_secret=config.twitter_credentials["access_token_secret"],
        )

    def search_tweets(self, nb_tweets: int = 10000):
        searched_tweets = []
        for x in config.search_tags:
            # TODO : search tweets created after a specific date
            searched_tweets += self.api.search_tweets(
                q=x, count=nb_tweets, tweet_mode="extended", result_type="recent"
            )
            searched_tweets += self.api.search_tweets(
                q=x, count=nb_tweets, tweet_mode="extended", result_type="popular"
            )
            searched_tweets += self.api.search_tweets(
                q=x, count=nb_tweets, tweet_mode="extended", result_type="mixed"
            )

        return searched_tweets

    def get_tweet_by_id(self, tweet_id: int):
        return self.api.get_status(tweet_id, tweet_mode="extended")

    def get_replies_count(self, user_screen_name, tweet_id):
        # TODO : why the replies_count is not the same as the count on front
        reply_count = 0
        for tweet in tweepy.Cursor(
                self.api.search_tweets, q=f"to:{user_screen_name}", tweet_mode="extended", since_id=tweet_id,
                count="9999"
        ).items():
            if hasattr(tweet, 'in_reply_to_status_id'):
                if tweet.in_reply_to_status_id == tweet_id:
                    reply_count += 1

        return reply_count
