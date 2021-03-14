
from abstract_command import AbstractCommand
import help
import general
import create_queue
import manage_access
import manage_queues
import modify_queue
import modify_registered
import update_queue

import inspect
from command_handler import CommandHandler

# required to initialize command handler
# if new commands file is added, it must be listed here
_command_modules = [help, general, create_queue, manage_queues, manage_access,
                    modify_queue, modify_registered, update_queue]


user_commands = [
    modify_queue.StudentFinished,
    modify_queue.AddMe,
    modify_queue.RemoveMe,
    update_queue.ShowCurrentQueue,
    update_queue.ShowCurrentAndNextStudent,
    manage_queues.SelectOtherQueue,
    help.ForAdmin
]

# None indicates empty line to be printed in help message
admin_commands = [
    create_queue.CreateSimple,
    create_queue.CreateRandom,
    None,
    manage_queues.SelectOtherQueue,
    manage_queues.DeleteQueue,
    manage_queues.RenameQueue,
    modify_queue.ShowMenu,
    None,
    modify_registered.ShowMenu,
    manage_access.AddAdmin,
    manage_access.RemoveAdmin,
]

# god commands will not show in help
god_commands = [
    help.ForGod,
    general.Start,
    general.Stop,
    general.ShowLogs,
    help.TelegramPreviewCommands,
    manage_queues.SaveQueuesToGoogleDrive
]

command_handler = CommandHandler()

# get all classes from modules
for module in _command_modules:
    for name, member in inspect.getmembers(module, inspect.isclass):
        if issubclass(member, AbstractCommand):
            command_handler.add_command(member)

if __name__ == '__main__':
    pass
