from queue_bot import commands
from queue_bot.commands import command
from queue_bot import language_pack


# this function requires callback query to be present
def handle_keyboard(update, bot):
    if update.callback_query is None:
        raise ValueError('update does not have any callback query')

    command_id, argument = commands.command.Command.parse_command(update.callback_query.data)

    # find command
    cmd = commands.command.Command.get_command_class(command_id)

    if argument is None:
        cmd.handle_reply_access(update, bot)
    else:
        cmd.handle_keyboard(update, bot)


def handle_text_command(update, command_entity, bot):
    command_string = update.message.text[command_entity.offset + 1: command_entity.length]
    cmd = commands.command.Command.get_command_by_name(command_string)

    if cmd is None:
        update.effective_message.reply_text(language_pack.unknown_command)
    else:
        cmd.handle_reply_access(update, bot)
