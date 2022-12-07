import pandas as pd
import os
import pathlib

import config


class CSV:
    def __init__(self):
        filename = f"giveaway_list_{config.twitter_account_tag.lower()}.csv"
        self.filename = f"{pathlib.Path().absolute()}/{filename}"
        self.index = "tweet_id"

    def create_giveaway_list(self):
        df = pd.DataFrame(
            columns=[
                "created_at",
                "updated_at",
                "treated_status",
                "tweet_created_date",
                "tweet_id",
                "tweet_text",
                "tweet_user_id",
                "tweet_user_screen_name",
                "tweet_user_name",
                "tweet_retweet_count",
                "tweet_favorite_count",
                "tweet_entities_user_mentions",
                "comment_status",
            ]
        )
        df.set_index(self.index)

        if not os.path.exists(self.filename):
            df.to_csv(self.filename, index=False, sep=";")

    def append(self, data):
        df = pd.read_csv(self.filename, sep=";")
        data = pd.DataFrame(data)
        df = pd.concat([df, data], ignore_index=True)
        df.to_csv(self.filename, index=False, sep=";")

    def get_df_data(self):
        df = pd.read_csv(self.filename, sep=";")
        df.set_index(self.index)
        return df
