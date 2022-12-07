# Giveaway Twitter Bot

This Twitter bot allows you to automatically participate in all contests on Twitter. <br>
It is able to follow, retweet, like and comment on tweets from Twitter accounts that run contests. <br>
It is fully configurable.

## Features
- Detect giveaways according to your keywords
- Ignore some tweets that contain certain words, tags or sentences
- Don't retweet tweets that have a few numbers of retweets (to avoid retweeting fake giveaways)
- Don't retweet old tweets 

## What's next?
- Automatically comment on tweets with a certain hashtag
- Automatically mention friends in comments
- Automatically remove friends that haven't created a new giveaway in a while

## Installation
1. Install Python 3.10 (I haven't tested it on other versions)
2. Create a virtual environment with `python -m venv .venv`
3. Activate the virtual environment with `source .venv/bin/activate`
4. Install the dependencies with `pipenv install`
5. Rename the `.env.example` file to `.env`
6. If you haven't a Twitter account, [create one](https://twitter.com/i/flow/signup)
7. Create a Twitter developer account [here](https://developer.twitter.com/en/apply-for-access)
8. Create a Twitter app on [Twitter Developer](https://developer.twitter.com/en/portal/dashboard) (Create Access tokens in `User authentication settings`)
9. Request elevated access levels [here](https://developer.twitter.com/en/portal/products/elevated)
10. Fill the required Twitter credentials variables in the `.env file` for the bot to work 
    - Consumer Key (API Key)
    - Consumer Secret (API Secret)
    - Bearer Token
    - Access Token
    - Access Token Secret
11. Configure the bot in the `.env` with the variables you want to change

## Start the bot
1. Activate the virtual environment with `source .venv/bin/activate`. If it's already activated, skip this step.
2. Run the bot with `python3 main.py`
3. Choose the option you want to run    
   - 1: Participate in contests and ask each tweet to comment
   - 2: Participate in contests and ignore all tweets that need to be commented
   - 3: Check all the tweets that you have already participated in and that need to be commented

## Warning
Twitter has limits on the number of actions you can do per day. <br>
To avoid being banned, respect the limitations of the variables in the .env configuration file <br>
If you exceed the limits, Twitter will block your account. <br>
You can check the limits [here](https://developer.twitter.com/en/docs/twitter-api/rate-limits).


