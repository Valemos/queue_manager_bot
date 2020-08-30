import bot_commands


class CommandHandler:

    @staticmethod
    def handle(update, queue, command_str):
        group, cmd = CommandHandler.parse_command(command_str)

        # find command
        group = getattr(cmd, group)
        cmd = getattr(group, cmd)

        cmd.handle(update, queue)

    @staticmethod
    def parse_command(command_str):
        try:
            items = command_str.split(':')
            return items[0], ''.join(items[1:])
        except Exception:
            return None, None
