import queue_bot.commands.command as commands

# these commands will be included in telegram command preview
# to generate help message for BotFather, print in telegram /help (for AcessLevel.GOD user)
import queue_bot.commands.create_queue.start_create
import queue_bot.commands.create_queue.start_create_random
import queue_bot.commands.general.start
import queue_bot.commands.general.stop
import queue_bot.commands.help.for_admin
import queue_bot.commands.help.for_god
import queue_bot.commands.help.preview_commans
import queue_bot.commands.manage_access.add_admin
import queue_bot.commands.manage_access.remove_admin
import queue_bot.commands.manage_queues.delete
import queue_bot.commands.manage_queues.rename
import queue_bot.commands.manage_queues.save_to_drive
import queue_bot.commands.modify_queue.add_me
import queue_bot.commands.modify_queue.remove_me
import queue_bot.commands.modify_queue.show_menu
import queue_bot.commands.modify_queue.student_finished
import queue_bot.commands.modify_registered.show_menu
import queue_bot.commands.select_queue
import queue_bot.commands.show_logs
import queue_bot.commands.update_queue.show_current
import queue_bot.commands.update_queue.show_status

user_commands = [
    queue_bot.commands.modify_queue.student_finished.StudentFinished,
    queue_bot.commands.modify_queue.add_me.AddMe,
    queue_bot.commands.modify_queue.remove_me.RemoveMe,
    queue_bot.commands.update_queue.show_queue.ShowCurrent,
    queue_bot.commands.update_queue.show_status.ShowStatus,
    queue_bot.commands.select_queue.SelectQueue,
    queue_bot.commands.help.for_admin.ForAdmin
]


# None indicates empty line to be printed in help message
admin_commands = [
    queue_bot.commands.create_queue.start_create.StartCreate,
    queue_bot.commands.create_queue.start_create_random.StartCreateRandom,
    None,
    queue_bot.commands.select_queue.SelectQueue,
    queue_bot.commands.manage_queues.delete_queue.Delete,
    queue_bot.commands.manage_queues.rename.Rename,
    queue_bot.commands.modify_queue.show_menu.ShowMenu,
    None,
    queue_bot.commands.modify_registered.show_menu.ShowMenu,
    queue_bot.commands.manage_access.add_admin.AddAdmin,
    queue_bot.commands.manage_access.remove_admin.RemoveAdmin,
    None,
    commands.CollectSubjectChoices.CreateNewCollectFile,
    commands.CollectSubjectChoices.StartChoose,
    commands.CollectSubjectChoices.StopChoose,
    commands.CollectSubjectChoices.GetExcelFile
]

# god commands will not show in help
god_commands = [
    queue_bot.commands.help.for_god.ForGod,
    queue_bot.commands.general.start.Start,
    queue_bot.commands.general.stop.Stop,
    queue_bot.commands.show_logs.ShowLogs,
    queue_bot.commands.help.preview_commans.PreviewCommands,
    queue_bot.commands.manage_queues.save_to_drive.SaveToDrive
]

# initialize all commands for telegram updater
all_commands = []
all_commands.extend(user_commands)
all_commands.extend([cmd for cmd in admin_commands if cmd is not None])
all_commands.extend(god_commands)


for cmd in all_commands:
    if cmd.command_name is None:
        raise ValueError('{0} name is None'.format(cmd.command_name))
