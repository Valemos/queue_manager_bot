from queue_bot.queue_telegram_bot import QueueBot
import sys

if len(sys.argv) > 1:
    my_bot = QueueBot(sys.argv[1])
else:
    my_bot = QueueBot()

my_bot.start()
