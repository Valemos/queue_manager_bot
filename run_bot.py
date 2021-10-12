import sys

from queue_bot.main_bot import QueueBot

if len(sys.argv) > 1:
    my_bot = QueueBot(sys.argv[1])
else:
    my_bot = QueueBot()

my_bot.start()
