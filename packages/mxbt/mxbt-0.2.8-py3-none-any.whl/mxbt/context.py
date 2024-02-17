from nio import MatrixRoom, Event, RoomMessageText
from dataclasses import dataclass, field
from typing import List

from .types.file import File
from .api import Api

@dataclass
class Context:
    """
    Event context class

    Parameters:
    -------------
    api: mxbt.Api
        Api object for sending events
    room: nio.MatrixRoom
        Event room object
    event: nio.Event
        Event object
    sender: str
        User id of event author
    event_id: str
        Id of received event
    body: str
        Body of received event
    command: str, optional
        If event is command - set command name here
    args: list[str], optional
        Command arguments
    substring: str, optional
        All arguments in one string
    mentions: list[str], optional
        List of all mentioned users in event
    """
    api: Api
    room: MatrixRoom
    room_id: str
    event: Event
    sender: str
    event_id: str
    body: str=str()
    command: str=str()
    args: List[str]=field(
        default_factory=lambda: list()
    )
    substring: str=str()
    mentions: List[str]=field(
        default_factory=lambda: list()
    )

    async def send(self, body: str | File,
                   use_html: bool=False,
                   mentions: list[str]=list()) -> None:
        """
        Send text or file to context room

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        await self.api.send(self.room_id, body, use_html, mentions)
        #await self.__send(body, use_html, False, False)

    async def reply(self, body: str | File,
                    use_html: bool=False,
                    mentions: list[str]=list()) -> None:
        """
        Reply context message with text or file

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        await self.api.reply(self.room_id, body,
                             self.event_id, use_html,
                             mentions)
        #await self.__send(body, use_html, True, False)

    async def edit(self, body: str | File,
                   use_html: bool=False,
                   mentions: list[str]=list()) -> None:
        """
        Edit context message with text or file

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        await self.api.edit(self.room_id, body, self.event_id, use_html, mentions)
        #await self.__send(body, use_html, False, True)
 
    async def delete(self, reason: str | None=None) -> None:
        """
        Delete context event

        Parameters:
        -------------
        reason: str | None - optional
            Reason, why message is deleted
        """
        await self.api.delete(
            self.room.room_id,
            self.event.event_id,
            reason
        )
    
    async def react(self, body: str) -> None:
        """
        Send reaction to context message.

        Parameters:
        --------------
        body : str
            Reaction emoji.
        """
        await self.api.send_reaction(
            self.room.room_id,
            self.event.event_id,
            body
        )

    async def ban(self, reason: str | None=None) -> None:
        """
        Ban sender of this event

        Parameters:
        -------------
        reason: str | None - optional
            Reason, why sender is banned
        """
        await self.api.ban(
            self.room.room_id,
            self.sender,
            reason
        )

    async def kick(self, reason: str | None=None) -> None:
        """
        Kick sender of this event

        Parameters:
        -------------
        reason: str | None - optional
            Reason, why sender is kicked
        """
        await self.api.kick(
            self.room.room_id,
            self.sender,
            reason
        )

    @staticmethod
    def __parse_command(message: RoomMessageText) -> tuple:
        args = message.body.split(" ")
        command = args[0]
        if len(args) > 1:
            args = args[1:]
        return command, args

    @staticmethod
    def __parse_mentions(message: RoomMessageText) -> list:
        mentions = list()
        content = message.source['content']
        if 'm.mentions' in content.keys():
            if 'user_ids' in content['m.mentions'].keys():
                mentions = content['m.mentions']['user_ids']
        return mentions

    @staticmethod
    def from_command(api: Api, room: MatrixRoom, message: RoomMessageText):
        command, args = Context.__parse_command(message)
        mentions = Context.__parse_mentions(message)
        return Context(
            api=api,
            room=room, 
            room_id=room.room_id,
            event=message,
            sender=message.sender,
            event_id=message.event_id,
            body=message.body,
            command=command,
            args=args,
            substring=' '.join(args),
            mentions=mentions
        )

    @staticmethod
    def from_text(api: Api, room: MatrixRoom, message: RoomMessageText):
        mentions = Context.__parse_mentions(message)
        return Context(
            api=api,
            room=room,
            room_id=room.room_id,
            event=message,
            sender=message.sender,
            event_id=message.event_id,
            body=message.body,
            mentions=mentions
        )

