
def get_command_list_help(cmd_list):
    """
    Collects data about commands in list and creates help message
    :param cmd_list: list of CommandGroup objects
    :return: str help message
    """

    # get max cmd length
    max_len = max((len(cmd.command_name) for cmd in cmd_list if cmd is not None)) + 3

    final_message = []
    for command in cmd_list:
        if command is not None:
            final_message.append(f"/{command.command_name:<{max_len}} - {command.description}")
        else:
            final_message.append('')

    return '\n'.join(final_message)
