import queue_bot.bot_commands as commands



available_commands = [
    commands.General.Start,
    commands.General.Stop,
    commands.General.ShowLogs,
    commands.Help.ForUser,
    commands.Help.ForAdmin,

    commands.ModifyCurrentQueue.AddMe,
    commands.ModifyCurrentQueue.RemoveMe,
    commands.ModifyCurrentQueue.StudentFinished,
    commands.UpdateQueue.ShowCurrent,

    commands.UpdateQueue.ShowCurrentAndNextStudent,
    commands.ManageQueues.CreateSimple,
    commands.ManageQueues.CreateRandom,
    commands.ModifyCurrentQueue.ShowMenu,
    commands.ModifyRegistered.ShowMenu,
    commands.ManageAccessRights.AddAdmin,
    commands.ManageAccessRights.RemoveAdmin,

    commands.CollectSubjectChoices.CreateNewCollectFile,
    commands.CollectSubjectChoices.StartChoose,
    commands.CollectSubjectChoices.StopChoose,
    commands.CollectSubjectChoices.ShowCurrentChoices,
    commands.CollectSubjectChoices.Choose,
    commands.CollectSubjectChoices.RemoveChoice,

    commands.ManageQueues.DeleteQueue,
    commands.ManageQueues.SelectOtherQueue,
    commands.CollectSubjectChoices.GetExcelFile
]

for cmd in available_commands:
    if cmd.command_name is None:
        raise ValueError('{0} name is None'.format(cmd.command_name))
