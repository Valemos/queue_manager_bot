from queue_bot import bot_commands


def handle(command_str, update, bot):
    group, cmd = bot_commands.CommandGroup.Command.parse_command(command_str)

    # find command
    group = getattr(bot_commands, group)
    cmd = getattr(group, cmd)

    cmd.handle(update, bot)
