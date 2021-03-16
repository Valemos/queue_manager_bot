from .command_handler import *
from .command_groups import *
import importlib

command_handler = CommandHandler()
command_handler.init_commands_from_module(importlib.import_module("queue_bot.commands"))
