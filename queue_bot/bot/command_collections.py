import queue_bot.commands as commands

# these commands will be included in telegram command preview
# to generate help message for BotFather, print in telegram /help (for AcessLevel.GOD user)

user_commands = [
    commands.modify_queue.student_finished.StudentFinished,
    commands.modify_queue.add_me.AddMe,
    commands.modify_queue.remove_me.RemoveMe,
    commands.update_queue.ShowCurrent,
    commands.update_queue.show_status.ShowStatus,
    commands.manage_queues.SelectQueue,
    commands.help.for_admin.ForAdmin
]


# None indicates empty line to be printed in help message
admin_commands = [
    commands.create_queue.start_create.StartCreate,
    commands.create_queue.start_create_random.StartCreateRandom,
    None,
    commands.manage_queues.SelectQueue,
    commands.manage_queues.Delete,
    commands.manage_queues.rename.Rename,
    commands.modify_queue.show_menu.ShowMenu,
    None,
    commands.modify_registered.show_menu.ShowMenu,
    commands.manage_access.add_admin.AddAdmin,
    commands.manage_access.remove_admin.RemoveAdmin,
]

# god commands will not show in help
god_commands = [
    commands.help.for_god.ForGod,
    commands.general.start.Start,
    commands.general.stop.Stop,
    commands.help.ShowLogs,
    commands.help.preview_commans.PreviewCommands,
    commands.manage_queues.save_to_drive.SaveToDrive
]

# initialize all commands for telegram updater
all_commands = []
all_commands.extend(user_commands)
all_commands.extend([cmd for cmd in admin_commands if cmd is not None])
all_commands.extend(god_commands)


for cmd in all_commands:
    if cmd.command_name is None:
        raise ValueError('{0} name is None'.format(cmd.command_name))
