import importlib

from .command_groups import *
from .command_handler import *

command_handler = CommandHandler()
command_handler.init_commands_from_module(importlib.import_module("queue_bot.commands"))
