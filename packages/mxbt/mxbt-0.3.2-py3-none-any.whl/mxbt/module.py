from enum import Enum
import inspect

def command(**kwargs):
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
        func.__command__ = kwargs
        return func
    return wrapper

class Event(Enum):
    onMessage = 0
    onMemberJoin = 1
    onMemberLeave = 2
    onReaction = 3
    onStartup = 4
    onCustomEvent = 5

def event(**kwargs):
    """
    Custom on_event event listener

    listener params:
    ------------------
    event_type: mxbt.module.Event - event type for listening. 
    event: nio.Event (optional) - custom event if event_type==onCustomEvent

    func params:
    ------------------
    room: nio.MatrixRoom
    event: nio.Event
    """
    def wrapper(func):
        func.__event__ = kwargs
        return func
    return wrapper

class Module:

    def __init__(self, bot) -> None:
        self.bot = bot
        self.__setup__()

    def add_command(self, method) -> None:
        kwargs = method.__command__
        @self.bot.listener.on_command(**kwargs)
        async def _(ctx) -> None:
            await method(ctx)

    def add_event(self, method) -> None:
        event_type = method.__event__['event_type']
        methods = {
            Event.onMessage : self.bot.listener.on_message,
            Event.onMemberJoin : self.bot.listener.on_member_join,
            Event.onMemberLeave : self.bot.listener.on_member_leave,
            Event.onReaction : self.bot.listener.on_reaction,
            Event.onStartup : self.bot.listener.on_startup,
        }
        if event_type in methods.keys():
            methods[event_type](method)
        elif event_type == Event.onCustomEvent:
            event = method.__event__['event']

            @self.bot.listener.on_custom_event(event)
            async def _(*args) -> None:
                await method(*args)

    def __setup__(self) -> None:
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for method_tuple in methods:
            method = method_tuple[1]
            if hasattr(method, '__command__'):
                self.add_command(method)
            elif hasattr(method, '__event__'):
                self.add_event(method)


