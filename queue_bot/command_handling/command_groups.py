import queue_bot.commands as commands

user_commands = [
    commands.StudentFinished,
    commands.AddMe,
    commands.RemoveMe,
    commands.ShowCurrentQueue,
    commands.ShowCurrentAndNextStudent,
    commands.SelectOtherQueue,
    commands.ForAdmin
]

# None indicates empty line to be printed in help message
admin_commands = [
    commands.CreateSimple,
    commands.CreateRandom,
    None,
    commands.SelectOtherQueue,
    commands.DeleteQueue,
    commands.RenameQueue,
    commands.ShowMenu,
    None,
    commands.ShowMenu,
    commands.AddAdmin,
    commands.RemoveAdmin,
]

# god command_handling will not show in help
god_commands = [
    commands.ForGod,
    commands.Start,
    commands.Stop,
    commands.ShowLogs,
    commands.TelegramPreviewCommands,
    commands.SaveQueuesToGoogleDrive
]

console_commands = user_commands + admin_commands + god_commands
console_commands = [cmd for cmd in console_commands if cmd is not None]
