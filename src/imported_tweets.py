import os


class ImportedTweets:

    def __init__(self):
        self.filename = "imported_tweet_ids.txt"
        self.create_file()

    def create_file(self):
        if not os.path.exists(self.filename):
            open(self.filename, "w").close()

    def add_tweet_id_to_file(self, tweet_id: str, tweet_ids: set):
        if str(tweet_id) not in tweet_ids:
            tweet_ids.add(tweet_id)
            with open(self.filename, "a") as f:
                f.write(f"{tweet_id},")
        return tweet_ids

    def get_tweet_ids_from_file(self):
        with open(self.filename, "r") as f:
            return set(f.read().strip(",").split(","))
