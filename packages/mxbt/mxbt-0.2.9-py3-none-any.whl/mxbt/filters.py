from nio import MatrixRoom

from .context import Context
from .match import Match

class Filter:

    @staticmethod
    def __find_context(args) -> Context | None:
        for arg in args:
            if isinstance(arg, Context):
                return arg
    
    @staticmethod
    def __find_context_body(args) -> tuple | None:
        for index, arg in enumerate(args):
            if isinstance(arg, MatrixRoom):
                return args[index:]

    @staticmethod
    def msgtype(values: list[str]):
        """
        Filter events with msgtype 

        filter params:
        ----------------
        values: list[str]
            list of accepted msgtypes
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if ctx.event.source['content']['msgtype'] in values:
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    _, event = body
                    if event.source['content']['msgtype'] in values:
                        await func(*args)
            return command_func
        return wrapper

    @staticmethod
    def has_text(values: list[str]):
        """
        Filter events with text in body

        filter params:
        ----------------
        values: list[str]
            list of accepted strings in body
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if Match.has_text(ctx.body, values):
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    _, event = body
                    if Match.has_text(event.body, values):
                        await func(*args)
            return command_func
        return wrapper

    @staticmethod
    def from_rooms(rooms: list):
        """
        from_rooms event filter

        filter params:
        ----------------
        rooms: list[str] 
            list of user_id, who is accepted to send event

        func params:
        --------------
        room: MatrixRoom,
        event: Event

        or 

        ctx: Context
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if Match.is_from_rooms(ctx.room.room_id, rooms):
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    room, _ = body
                    if Match.is_from_rooms(room.room_id, rooms):
                        await func(*args)
            return command_func
        return wrapper

    @staticmethod
    def from_users(users: list):
        """
        from_users event filter

        filter params:
        ----------------
        users: list[str]
            list of user_id, who is accepted to send event

        func params:
        --------------
        room: MatrixRoom,
        event: Event

        or 

        ctx: Context
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if Match.is_from_users(ctx.sender, users):
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    _, message = body
                    if Match.is_from_users(message.sender, users):
                        await func(*args)
            return command_func
        return wrapper

    @staticmethod
    def sender_can_ban():
        """
        sender_can_ban event filter

        func params:
        --------------
        room: MatrixRoom,
        event: Event

        or 

        ctx: Context
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if Match.can_ban(ctx.room, ctx.sender):
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    room, message = body
                    if Match.can_ban(room, message.sender):
                        await func(*args)
            return command_func
        return wrapper

    @staticmethod
    def sender_can_kick():
        """
        sender_can_kick event filter

        func params:
        --------------
        room: MatrixRoom,
        event: Event

        or 

        ctx: Context
        """
        def wrapper(func):
            async def command_func(*args) -> None:
                ctx = Filter.__find_context(args)
                if not ctx is None:
                    if Match.can_kick(ctx.room, ctx.sender):
                        await func(*args)
                else:
                    body = Filter.__find_context_body(args)
                    if body is None: return
                    room, message = body
                    if Match.can_kick(room, message.sender):
                        await func(*args)
            return command_func
        return wrapper


