from queue_bot.bot.parsers import parse_command_name


class CommandMappingMeta(type):

    __last_command_id__: int = 0
    __command_id_dict__: dict = {}
    __id_command_dict__: dict = {}
    __name_command__: dict = {}

    command_name: str

    def __init__(cls, name, bases, namespace) -> None:
        super().__init__(name, bases, namespace)

        if not hasattr(cls, "command_name"):
            # this means, that command does not need to be indexed
            return

        if cls.command_name is not None:
            cls.__name_command__[cls.command_name] = cls

        command_id = str(cls.__last_command_id__)
        cls.__command_id_dict__[cls] = command_id
        cls.__id_command_dict__[command_id] = cls
        cls.__last_command_id__ += 1

        # also for every command we must set if we need to check for private chat

    def query(cls, args=None):
        if args is None:
            return cls.__command_id_dict__[cls]
        else:
            return cls.__command_id_dict__[cls] + '#' + str(args)

    def get_command_class(cls, command_id: str):
        return cls.__id_command_dict__[command_id]

    def get_command_by_name(cls, command_string):
        name = parse_command_name(command_string)
        if name in cls.__name_command__:
            return cls.__name_command__[name]
        else:
            return None
