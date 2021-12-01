from queue_bot import commands
from queue_bot.commands import command
from queue_bot import language_pack


# this function requires callback query to be present
from queue_bot.commands.misc.logging import log_bot_user
from queue_bot.error import InsufficientAccess


def handle_keyboard(update, bot):
    if update.callback_query is None:
        raise ValueError('update does not have any callback query')

    command_id, argument = commands.command.Command.parse_command(update.callback_query.data)

    # find command
    cmd = commands.command.Command.get_command_class(command_id)
    if cmd is None:
        raise ValueError(f'incorrect keyboard command id ({command_id})!')

    try:
        if argument is None:
            cmd.handle_reply_access(update, bot)
        else:
            cmd.handle_keyboard_access(update, bot)
    except InsufficientAccess:
        _handle_insufficient_access(bot, update, cmd)


def handle_text_command(update, command_entity, bot):
    command_string = update.message.text[command_entity.offset + 1: command_entity.length]
    cmd = commands.command.Command.get_command_by_name(command_string)

    if cmd is None:
        update.effective_message.reply_text(language_pack.unknown_command)
        return

    try:
        cmd.handle_reply_access(update, bot)
    except InsufficientAccess:
        _handle_insufficient_access(bot, update, cmd)


def _handle_insufficient_access(bot, update, cmd):
    log_bot_user(update, bot, 'tried to get access to {0} command', cmd.access_requirement.name)
    if update.message is not None:
        update.message.reply_text(language_pack.permission_denied)
    else:
        update.effective_chat.send_message(language_pack.permission_denied)
