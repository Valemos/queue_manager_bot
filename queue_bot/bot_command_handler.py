from queue_bot import bot_commands


# this function requires callback query to be present
def handle(update, bot):
    if update.callback_query is None:
        raise ValueError('update does not have any callback query')

    group, cmd = bot_commands.CommandGroup.Command.parse_command(update.callback_query.data)

    # find command
    group = getattr(bot_commands, group)
    cmd = getattr(group, cmd)

    if bot_commands.CommandGroup.Command.get_arguments(update.callback_query.data) is None:
        cmd.handle_command(update, bot)
    else:
        cmd.handle_keyboard(update, bot)
