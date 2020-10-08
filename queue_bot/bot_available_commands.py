import queue_bot.bot_commands as commands

# these commands will be included in telegram command preview
# to generate help message for BotFather, print in telegram /help (for AcessLevel.GOD user)
user_commands = [
    commands.ModifyCurrentQueue.StudentFinished,
    commands.ModifyCurrentQueue.AddMe,
    commands.ModifyCurrentQueue.RemoveMe,
    commands.UpdateQueue.ShowCurrentQueue,
    commands.UpdateQueue.ShowCurrentAndNextStudent,
    commands.CollectSubjectChoices.Choose,
    commands.CollectSubjectChoices.RemoveChoice,
    commands.CollectSubjectChoices.ShowCurrentChoices,
    commands.CollectSubjectChoices.StartChoose,
    commands.CollectSubjectChoices.StopChoose,
    commands.Help.ForAdmin
]


# None indicates empty line to be printed in help message
admin_commands = [
    commands.CreateQueue.CreateSimple,
    commands.CreateQueue.CreateRandom,
    None,
    commands.ManageQueues.SelectOtherQueue,
    commands.ManageQueues.DeleteQueue,
    commands.ManageQueues.RenameQueue,
    commands.ModifyCurrentQueue.ShowMenu,
    None,
    commands.ModifyRegistered.ShowMenu,
    commands.ManageAccessRights.AddAdmin,
    commands.ManageAccessRights.RemoveAdmin,
    None,
    commands.CollectSubjectChoices.CreateNewCollectFile,
    commands.CollectSubjectChoices.StartChoose,
    commands.CollectSubjectChoices.StopChoose,
    commands.CollectSubjectChoices.GetExcelFile
]

# god commands will not show in help
god_commands = [
    commands.General.Start,
    commands.General.Stop,
    commands.General.ShowLogs,
    commands.Help.TelegramPreviewCommands
]

# initialize all commands for telegram updater
all_commands = []
all_commands.extend(user_commands)
all_commands.extend([cmd for cmd in admin_commands if cmd is not None])
all_commands.extend(god_commands)


for cmd in all_commands:
    if cmd.command_name is None:
        raise ValueError('{0} name is None'.format(cmd.command_name))
