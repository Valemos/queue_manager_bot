
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

all_commands = user_commands + admin_commands + god_commands
all_commands = [cmd for cmd in all_commands if cmd is not None]


def get_command_list_help(cmd_list):
    """
    Collects data about commands in list and creates help message
    :param cmd_list: list of CommandGroup.CommandGroup objects
    :return: str help message
    """

    # get max cmd length
    max_len = max((len(cmd.command_name) for cmd in cmd_list if cmd is not None)) + 3

    final_message = []
    for command in cmd_list:
        if command is not None:
            final_message.append(f"/{command.command_name:<{max_len}} - {command.description}")
        else:
            final_message.append('')

    return '\n'.join(final_message)


# initialize command handler with all command classes
command_handler = CommandHandler()

# get all classes from modules
for module in _command_modules:
    for name, member in inspect.getmembers(module, inspect.isclass):
        if issubclass(member, AbstractCommand):
            command_handler.add_command(member)
