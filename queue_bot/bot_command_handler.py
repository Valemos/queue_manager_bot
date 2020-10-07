from queue_bot import bot_commands


# this function requires callback query to be present
def handle_keyboard(update, bot):
    if update.callback_query is None:
        raise ValueError('update does not have any callback query')

    index, argument = bot_commands.CommandGroup.Command.parse_command(update.callback_query.data)

    # find command
    cmd = bot_commands.CommandGroup.Command.get_command_class(index)

    if argument is None:
        cmd.handle_command_access(update, bot)
    else:
        cmd.handle_keyboard(update, bot)


def handle_text_command(update, command_entity, bot):
    command_string = update.message.text[command_entity.offset + 1: command_entity.length]
    cmd = bot_commands.CommandGroup.Command.get_command_by_name(command_string)

    if cmd is None:
        update.effective_message.reply_text(bot.language_pack.unknown_command)
    else:
        cmd.handle_command_access(update, bot)
