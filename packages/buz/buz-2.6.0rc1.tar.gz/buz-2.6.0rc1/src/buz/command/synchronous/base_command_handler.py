from typing import Type, get_type_hints

from buz.command import Command
from buz.command.synchronous.command_handler import CommandHandler


class BaseCommandHandler(CommandHandler):
    @classmethod
    def fqn(cls) -> str:
        return f"command_handler.{cls.__module__}.{cls.__name__}"

    @classmethod
    def handles(cls) -> Type[Command]:
        handle_types = get_type_hints(cls.handle)

        if "command" not in handle_types:
            raise TypeError("command parameter not found in handle method")

        if not issubclass(handle_types["command"], Command):
            raise TypeError("command parameter is not an buz.command.Command subclass")

        return handle_types["command"]
