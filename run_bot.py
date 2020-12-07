import sys

from queue_bot.bot_telegram_queue import QueueBot

if len(sys.argv) > 1:
    my_bot = QueueBot(sys.argv[1])
else:
    my_bot = QueueBot()

my_bot.start()
