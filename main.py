import time
from src.print import Print
from src.giveway_bot import GiveawayBot
from src.enum.run_action import RunAction

while True:
    try:
        giveaway_bot = GiveawayBot()
        giveaway_bot.import_latest_tweets()
        giveaway_bot.update_tweets_counters()

        while True:
            Print.blue("What action do you want to do ?")
            Print.blue(f"{RunAction.FULL.value} : Run the bot and ask to comment the tweet when it's required")
            Print.blue(f"{RunAction.WITHOUT_COMMENT.value} : Run the bot and ignore comment request")
            Print.blue(f"{RunAction.ONLY_COMMENT.value} : Check all tweets that require a comment")

            answer = input()
            if answer not in [
                str(RunAction.FULL.value),
                str(RunAction.WITHOUT_COMMENT.value),
                str(RunAction.ONLY_COMMENT.value)
            ]:
                Print.red("Please enter a valid answer")
                continue
            else:
                break

        giveaway_bot.run(int(answer))

    except Exception as e:
        Print.red(str(e), bold=True)
        break

    # This is here in case there were not tweets checked
    time.sleep(5)
