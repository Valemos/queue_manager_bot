from HelperBot import QueueBot
from flask import Flask, request


bot_token = "948057504:AAH3Le3JvcPsSW-16M8bUsVZmAICjbqL6Js"

my_bot = QueueBot(bot_token)
my_bot.start()