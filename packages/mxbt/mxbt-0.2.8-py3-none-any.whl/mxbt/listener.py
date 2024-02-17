from nio import (MatrixRoom, RoomMessageText,
                 RoomMessage, UnknownEvent,
                 InviteMemberEvent)

from .types.command import Command
from .context import Context
from .match import Match

class Listener:

    def __init__(self, bot) -> None:
        self._bot = bot
        self._registry = list()
        self._startup_registry = list()
        self._commands = list()

    def _reg_command(self, prefix: str, aliases: list[str]) -> None:
        self._commands.append(Command(prefix, aliases))

    def _reg_event(self, func, event) -> None:
        self._registry.append([func, event])

    def _get_command_prefix(self, **kwargs) -> str:
        if not 'prefix' in kwargs.keys():
            return self._bot.prefix
        else:
            return kwargs['prefix']

    def _get_command_name(self, prefix: str, body: str) -> str:
        return body.split(" ")[0].replace(prefix, "")

    def get_commands(self) -> list:
        return self._commands.copy()

    def on_custom_event(self, event):

        def wrapper(func) -> None:
            if [func, event] in self._registry:
                func()
            else:
                self._reg_event(func, event)

        return wrapper

    def on_message(self, func) -> None:
        """
        on_message event listener

        func params:
        --------------
        room: MatrixRoom
        event: RoomMessage
        """
        if [func, RoomMessage] in self._registry:
            func()
        else:
            self._reg_event(func, RoomMessage)

    def on_message_text(self, func) -> None:
        """
        on_message_text event listener

        func params:
        --------------
        room: MatrixRoom
        event: RoomMessageText
        """
        if [func, RoomMessageText] in self._registry:
            func()
        else:
            self._reg_event(func, RoomMessageText)

    def on_member_join(self, func) -> None:
        """
        on_member_join event listener

        func params:
        --------------
        room: MatrixRoom
        event: InviteMemberEvent
        """
        async def wrapper(room: MatrixRoom, event: InviteMemberEvent) -> None:
            if event.membership == 'join':
                await func(room, event)
        self._reg_event(wrapper, InviteMemberEvent)

    def on_member_leave(self, func) -> None:
        """
        on_member_leave event listener

        func params:
        --------------
        room: MatrixRoom
        event: InviteMemberEvent
        """
        async def wrapper(room: MatrixRoom, event: InviteMemberEvent) -> None:
            if event.membership == 'leave':
                await func(room, event)
        self._reg_event(wrapper, InviteMemberEvent)

    def on_command(self, **kwargs):
        """
        Custom on_command event listener

        listener params:
        ------------------
        aliases: list[str] - list of command aliases
        prefix: str, optional - custom command prefix (empty - use standart bot prefix)

        func params:
        ------------------
        ctx: mxbt.Context
        """
        def wrapper(func):
            prefix = self._get_command_prefix(**kwargs) 
            self._reg_command(prefix, kwargs['aliases'])

            async def command_func(room, event: RoomMessageText) -> None:
                if not event.body.startswith(prefix):
                    return

                match = Match(room, event, self._bot)
                name = self._get_command_name(prefix, event.body)
                if name in kwargs['aliases']:
                    if self._bot.selfbot:
                        if not match.is_from_self():
                            return
                    else:
                        if match.is_from_self():
                            return
                    await func(Context.from_command(self._bot.api, room, event))
            self._reg_event(command_func, RoomMessageText)
            return command_func
        return wrapper

    def on_reaction(self, func) -> None:
        async def new_func(room, event) -> None:
            if event.type == "m.reaction":
                await func(room, event,
                           event.source['content']['m.relates_to']['key'])

        self._reg_event(new_func, UnknownEvent)

    def on_startup(self, func) -> None:
        if func in self._startup_registry:
            func()
        else:
            self._startup_registry.append(func)


