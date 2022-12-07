from dotenv import dotenv_values

config = dotenv_values(".env")


def convert_to_bool(string: str) -> bool:
    if string.lower() in ["1", "true"]:
        return True
    return False


def get_words_from_string(string_to_list: str) -> list:
    string_to_list = string_to_list.lower()
    string_to_list = string_to_list.strip("|")

    separators = (",", ":")
    for separator in separators:
        string_to_list.replace(separator, "|")

    return string_to_list.split("|")


twitter_credentials = {
    "client_id": config["API_KEY"],
    "client_secret": config["API_KEY_SECRET"],
    "bearer_token": config["BEARER_TOKEN"],
    "access_token": config["ACCESS_TOKEN"],
    "access_token_secret": config["ACCESS_TOKEN_SECRET"]
}

twitter_account_tag = config["TWITTER_ACCOUNT_TAG"]
search_tags = get_words_from_string(config["SEARCH_TAGS"])
banned_user_tags = get_words_from_string(config["BANNED_USER_TAGS"])
banned_user_name_keywords = get_words_from_string(config["BANNED_USER_NAME_KEYWORDS"])
banned_words = get_words_from_string(config["BANNED_WORDS"])
banned_strings = get_words_from_string(config["BANNED_STRINGS"])
follow_words = get_words_from_string(config["FOLLOW_WORDS"])
retweet_words = get_words_from_string(config["RETWEET_WORDS"])
like_words = get_words_from_string(config["LIKE_WORDS"])
comment_words = get_words_from_string(config["COMMENT_WORDS"])
follow_wait_seconds = int(config["FOLLOW_WAIT_SECONDS"])
retweet_wait_seconds = int(config["RETWEET_WAIT_SECONDS"])
like_wait_seconds = int(config["LIKE_WAIT_SECONDS"])
minimum_retweets = int(config["MINIMUM_RETWEETS"])
update_tweets_counters_minutes = int(config["UPDATE_TWEETS_COUNTERS_MINUTES"])
max_friends = int(config["MAX_FRIENDS"])
allow_comment = convert_to_bool(config["ALLOW_COMMENT"])
print_in_colors = convert_to_bool(config["PRINT_IN_COLORS"])
