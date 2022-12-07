import ast
import time
from datetime import timedelta

import pandas as pd

import config
from src.print import Print
from src.enum.treated_status import TreatedStatus
from src.enum.comment_status import CommentStatus
from src.enum.run_action import RunAction
from src.twitter.twitter_api import TwitterApi
from src.csv import CSV
from src.date import Date


class GiveawayBot:

    def __init__(self):
        self.csv = CSV()
        self.csv.create_giveaway_list()
        self.twitter = TwitterApi()
        self.limit_follow = 50
        self.limit_retweet = 50
        self.limit_like = 50
        self.limit_minutes = 15

        user = self.twitter.api.get_user(screen_name=config.twitter_account_tag)
        self.username = user.screen_name
        self.user_id = user.id
        self.friends_count = user.friends_count
        self.friends = []
        self.action = None

    def run(self, action: int):
        self.action = action

        giveaway_list = self.csv.get_df_data()

        if action == RunAction.ONLY_COMMENT.value:
            return self.action_only_comment(giveaway_list)

        return self.action_treat_tweets(giveaway_list)

    def action_treat_tweets(self, giveaway_list):
        # get values from csv where treated status in not treated
        giveaway_list_untreated = giveaway_list[giveaway_list.treated_status == TreatedStatus.NOT_TREATED.value]
        Print.blue(f"Started Analyzing ({Date.formatted()})")
        nb_remaining_tweets = len(giveaway_list_untreated) + 1

        for index, row in giveaway_list_untreated.iterrows():
            nb_remaining_tweets -= 1

            Print.blue(f"Remaining tweets: {nb_remaining_tweets}")
            Print.blue(f"Analyzing tweet {self.get_tweet_url(row)}")

            if not self.has_minimum_retweet(giveaway_list, row):
                continue

            if self.has_banned_word(giveaway_list, row):
                continue

            if self.has_banned_user(giveaway_list, row):
                continue

            self.like_tweet(row)

            # Retweet
            self.retweet_tweet(row)

            self.follow_users(row)

            self.comment_tweet(giveaway_list, row)
            self.tweet_is_treated(giveaway_list, row)

        Print.green(f"Finished Analyzing ({str(len(giveaway_list))} tweets analyzed)")

    def action_only_comment(self, giveaway_list):
        # get all tweets where comment_status is required
        giveaway_list_comment_required = giveaway_list[giveaway_list.comment_status == CommentStatus.REQUIRED.value]
        giveaway_commented = 0
        remaining_tweets = len(giveaway_list_comment_required) + 1

        for index, row in giveaway_list_comment_required.iterrows():
            remaining_tweets -= 1
            Print.blue(f"{remaining_tweets} remaining tweets to comment")

            if not self.has_minimum_retweet(giveaway_list_comment_required, row):
                continue
            if self.has_banned_word(giveaway_list_comment_required, row):
                continue
            if self.has_banned_user(giveaway_list_comment_required, row):
                continue

            self.comment_tweet(giveaway_list, row)
            giveaway_commented += 1

        Print.green(f"{giveaway_commented} tweets commented")
        return

    def import_latest_tweets(self):
        Print.blue("Import latest tweets")

        csv_data = self.csv.get_df_data()

        tweets_found = self.twitter.search_tweets()
        tweets_to_add = []

        for tweet in tweets_found:
            # if it's a retweet, we get the original tweet
            while True:
                if hasattr(tweet, "retweeted_status"):
                    if tweet.retweeted_status is not None:
                        tweet = tweet.retweeted_status
                    else:
                        break

                if hasattr(tweet, "in_reply_to_status_id"):
                    if tweet.in_reply_to_status_id is not None:
                        try:
                            tweet = self.twitter.get_tweet_by_id(tweet.in_reply_to_status_id)
                        except Exception as e:
                            Print.red(f"Can't getting the original tweet from the tweet id: {tweet.id}")
                            break
                        continue
                    else:
                        break
                else:
                    break

            data_to_write = {
                "created_at": Date.now(),
                "updated_at": Date.now(),
                "treated_status": TreatedStatus.NOT_TREATED.value,
                "tweet_created_date": pd.to_datetime(tweet.created_at).normalize(),
                "tweet_id": tweet.id,
                "tweet_text": tweet.full_text,
                "tweet_user_id": tweet.user.id,
                "tweet_user_screen_name": tweet.user.screen_name,
                "tweet_user_name": tweet.user.name,
                "tweet_retweet_count": int(tweet.retweet_count),
                "tweet_favorite_count": int(tweet.favorite_count),
                "tweet_entities_user_mentions": tweet.entities["user_mentions"],
                "comment_status": CommentStatus.WAITING.value,
            }

            tweets_to_add.append(data_to_write)

        tweets_to_add = pd.DataFrame(tweets_to_add)
        tweets_to_add.set_index(self.csv.index)
        tweets_to_add.drop_duplicates(keep="first", inplace=True, ignore_index=True, subset=[self.csv.index])
        tweets_to_add = tweets_to_add[~tweets_to_add.tweet_id.isin(csv_data.tweet_id)]

        self.csv.append(tweets_to_add)

        Print.green(f"{len(tweets_to_add)} tweets imported")

    def update_tweet_counters(self, csv_data, row, save=True):
        try:
            tweet = self.twitter.get_tweet_by_id(row.tweet_id)
            if tweet is not None:
                csv_data.loc[csv_data.tweet_id == row.tweet_id, "tweet_retweet_count"] = tweet.retweet_count
                csv_data.loc[csv_data.tweet_id == row.tweet_id, "tweet_favorite_count"] = tweet.favorite_count
                csv_data.loc[csv_data.tweet_id == row.tweet_id, "updated_at"] = Date.now()

        except Exception as e:
            Print.red(e)
            self.tweet_is_removed(csv_data, row)

        if save:
            csv_data.to_csv(self.csv.filename, index=False, sep=";")
        else:
            return csv_data

    def update_tweets_counters(self):
        Print.blue("Update tweets counters")

        csv_data = self.csv.get_df_data()
        # get only tweets that don't have the minimum retweet count
        csv_data_untreated = csv_data[csv_data.treated_status.eq(TreatedStatus.REMOVED.value)]

        # get only tweets that are created before 2 days
        csv_data_untreated = csv_data_untreated[
            csv_data_untreated.tweet_created_date >= pd.to_datetime(Date.now() - timedelta(days=2))]

        # get only tweets that updated date is lower than update_tweets_counters_minutes
        csv_data_untreated = csv_data_untreated[
            csv_data_untreated.updated_at <= pd.to_datetime(
                Date.now() - timedelta(minutes=config.update_tweets_counters_minutes)
            )
            ]

        Print.green(f"{len(csv_data_untreated)} tweets to update")

        untreated_loop = 0

        for index, row in csv_data_untreated.iterrows():
            untreated_loop += 1
            Print.white(f"Update tweet {row.tweet_id}")
            csv_data = self.update_tweet_counters(csv_data, row, save=False)

            if untreated_loop % 10 == 0:
                Print.blue("Save tweets")
                csv_data.to_csv(self.csv.filename, index=False, sep=";")

        csv_data.to_csv(self.csv.filename, index=False, sep=";")

    def has_minimum_retweet(self, giveaway_list, row):
        if row.tweet_retweet_count < config.minimum_retweets:
            self.tweet_is_ignored(giveaway_list, row)
            return False
        return True

    def has_banned_user(self, giveaway_list, row):
        if row.tweet_user_screen_name.lower() in config.banned_user_tags or any(
                x in row.tweet_user_name.lower() for x in config.banned_user_name_keywords
        ):
            self.tweet_is_banned(giveaway_list, row, message=f"Banned user found: {row.tweet_user_screen_name}")
            self.twitter.client.unfollow_user(target_user_id=row.tweet_user_id)
            return True
        return False

    def has_banned_word(self, giveaway_list, row):
        for word in config.banned_words:
            word_list = row.tweet_text.lower().split()

            if word in word_list:
                self.tweet_is_banned(giveaway_list, row, message=f"Banned word found in tweet: {word}")
                return True

        for string in config.banned_strings:
            if string in row.tweet_text.lower():
                self.tweet_is_banned(giveaway_list, row, message=f"Banned string found in tweet: {string}")
                return True

        return False

    def follow_users(self, row):
        if any(x in row.tweet_text.lower() for x in config.follow_words):
            # If the tweet contains any follow_tags, it automatically follows all the users mentioned in the tweet (
            # if there's any) + the author

            friends_count = self.twitter.api.get_user(screen_name=self.username).friends_count

            while True:
                if friends_count > config.max_friends:
                    self.unfollow_users(friends_count)
                else:
                    break

            friends_added = []

            self.twitter.client.follow_user(target_user_id=row.tweet_user_id)
            Print.white(f"Followed! @{row.tweet_user_screen_name}")
            friends_added.append(row.tweet_user_screen_name)

            time.sleep(config.follow_wait_seconds)

            user_mentions = ast.literal_eval(row.tweet_entities_user_mentions)

            for user_mention in user_mentions:
                user_mention_screen_name = user_mention["screen_name"]

                # If the user is not already followed
                if user_mention_screen_name in self.friends or user_mention_screen_name in friends_added:
                    continue

                self.twitter.client.follow_user(target_user_id=user_mention["id"])
                Print.white(f"Followed! @{user_mention_screen_name}")

                time.sleep(config.follow_wait_seconds)
                friends_added.append(user_mention_screen_name)

            self.friends.extend(friends_added)

    def unfollow_users(self, friends_nb: int):
        Print.red(f"Too many friends, removing some friends")

        # TODO : unfollow friends_nb older friends from giveaway_list.csv than have not been new giveaway

        # Twitter sets a limit of not following more than 2k people in total (varies depending on followers)
        # while friends_nb < twitter.api.get_user(screen_name=username).friends_count:
        #     try:
        #         x = friends[random.randint(0, len(friends) - 1)]
        #         print(f"Unfollowed: @{x}")
        #         friend = twitter.api.get_user(screen_name=x)
        #         twitter.client.unfollow_user(target_user_id=friend.screen_name)
        #         friends.remove(x)
        #     except Exception as e:
        #         Print.red(e)
        pass

    def retweet_tweet(self, row):
        if any(x in row.tweet_text.lower().split() for x in config.retweet_words):
            try:
                self.twitter.client.retweet(tweet_id=row.tweet_id)
                Print.white(f"Retweeted!")
                time.sleep(config.retweet_wait_seconds)

            except Exception as e:
                if "retweeted" not in str(e):
                    # If is not a problem of already retweeted
                    Print.red(str(e), bold=True)
                    return False

    def comment_tweet(self, giveaway_list, row):
        # TODO : comment tweet auto (select random friend in my list)

        # process if tweet contains word in config.comment_tags
        word_list = row.tweet_text.lower().split()

        for word in config.comment_words:
            if word in word_list:
                Print.blue(f"Word found: '{word}'")

                if self.action == RunAction.WITHOUT_COMMENT.value:
                    self.tweet_comment_is_required(giveaway_list, row)
                    return True

                Print.blue(f"Please comment the tweet: {self.get_tweet_url(row)}")
                while True:
                    Print.blue("Type 'y' to confirm the comment, or 'n' to ignore the comment for this tweet : ")
                    answer = input()
                    if answer == "y":
                        self.tweet_is_commented(giveaway_list, row, f"Commented!")
                        return True
                    elif answer == "n":
                        self.tweet_is_not_commented(giveaway_list, row, f"Comment ignored")
                        return True

        # TODO : process if comments nb are > 90% of retweet count
        # elif tweet.retweet_count >= 0 and tweet.reply_count > (tweet.retweet_count * 0.9):
        #     data_to_write["comment_status"] = CommentStatus.TO_COMMENT.value
        else:
            self.tweet_comment_is_not_required(giveaway_list, row, f"Comment not required")

    def like_tweet(self, row):
        try:
            # If the tweets contains any like_tags, it automatically likes the tweet
            if any(x in row.tweet_text.lower() for x in config.like_words):
                self.twitter.client.like(tweet_id=row.tweet_id)
                Print.white(f"Liked!")
                time.sleep(config.like_wait_seconds)
        except:
            pass

    def tweet_is_banned(self, giveaway_list: pd.DataFrame, row, message: str = "Banned word found in tweet"):
        Print.red(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'treated_status'] = TreatedStatus.BANNED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_is_ignored(
        self,
        giveaway_list: pd.DataFrame, row, message: str = f"Retweet less than {config.minimum_retweets}"
    ):
        Print.red(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'treated_status'] = TreatedStatus.IGNORED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_is_removed(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet removed!"):
        Print.red(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'treated_status'] = TreatedStatus.REMOVED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_is_treated(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet treated!"):
        Print.green(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'treated_status'] = TreatedStatus.TREATED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_is_commented(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet treated!"):
        Print.white(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'comment_status'] = CommentStatus.COMMENTED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_is_not_commented(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet treated!"):
        Print.white(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'comment_status'] = CommentStatus.NOT_COMMENTED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_comment_is_not_required(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet treated!"):
        Print.blue(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'comment_status'] = CommentStatus.NOT_REQUIRED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def tweet_comment_is_required(self, giveaway_list: pd.DataFrame, row, message: str = "Tweet require a comment!"):
        Print.red(message)
        giveaway_list.loc[giveaway_list.tweet_id == row.tweet_id, 'comment_status'] = CommentStatus.REQUIRED.value
        giveaway_list.to_csv(self.csv.filename, index=False, sep=";")

    def get_tweet_url(self, row):
        return f"https://twitter.com/{row.tweet_user_screen_name}/status/{row.tweet_id}"
