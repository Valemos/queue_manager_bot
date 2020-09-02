import bot_commands


class CommandHandler:

    @staticmethod
    def handle(command_str, update, bot):
        group, cmd = CommandHandler.parse_command(command_str)

        # find command
        group = getattr(bot_commands, group)
        cmd = getattr(group, cmd)

        cmd.handle(update, bot)

    @staticmethod
    def parse_command(command_str):
        try:
            # __qualname__ returns class in format Class.Subclass and query formed only from it
            items = command_str.split('.')
            return items[0], ''.join(items[1:])
        except Exception:
            return None, None
