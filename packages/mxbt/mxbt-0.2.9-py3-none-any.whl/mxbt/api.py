from nio import AsyncClient, Event, MatrixRoom, OlmUnverifiedDeviceError, AsyncClientConfig, RoomGetEventResponse, RoomMessageAudio, RoomMessageFile, RoomMessageImage, RoomMessageText, RoomMessageVideo, RoomSendResponse
from nio.crypto import ENCRYPTION_ENABLED
from typing import List, Union, Tuple 
import markdown
import aiohttp
import json
import nio
import os
import re

from .types.file import File
from .utils import info, error
#from .context import Context

def split_mxid(mxid: str) -> Union[Tuple[str, str], Tuple[None, None]]:
    # s = mxid.split(':')
    # if len(s) != 2 or s[0][0] != '@':
    #     return None, None
    # s[0] = s[0][1:]
    match = re.match(
        r'@(?P<localpart>[^:]*):(?P<hostname>(?P<ipv4>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?P<ipv6>\[[\da-fA-F:.]{2,45}\])|(?P<dns>[a-zA-Z\d\-.]{1,255}))(?P<port>:\d{1,5})?',
        mxid)
    if match is None:
        return None, None
    return match.group('localpart'), match.group('hostname')


class Api:

    def __init__(self, creds) -> None:
        self.creds = creds
        self.async_client: AsyncClient | None = None

    async def login(self):
        """
        Login the client to the homeserver

        Implementation from:
        https://codeberg.org/imbev/simplematrixbotlib/src/branch/master/simplematrixbotlib/api.py

        """

        if not self.creds.homeserver:
            raise ValueError("Missing homeserver")
        if not self.creds.username:
            raise ValueError("Missing Username")
        if not (self.creds.password or self.creds.login_token
                or self.creds.access_token):
            raise ValueError(
                "Missing password, login token, access token. "
                "Either password, login token or access token must be provided"
            )

        client_config = AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=ENCRYPTION_ENABLED)
        store_path = "./store"
        os.makedirs(store_path, mode=0o750, exist_ok=True)
        self.async_client = AsyncClient(homeserver=self.creds.homeserver,
                                        user=self.creds.username,
                                        device_id=self.creds.device_id,
                                        store_path=store_path,
                                        config=client_config)

        if self.creds.access_token:
            self.async_client.access_token = self.creds.access_token

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.creds.homeserver}/_matrix/client/r0/account/whoami?access_token={self.creds.access_token}'
                ) as response:
                    if isinstance(response, nio.responses.LoginError):
                        raise Exception(response)

                    r = json.loads(
                        (await
                         response.text()).replace(":false,", ":\"false\","))
                    # This assumes there was an error that needs to be communicated to the user. A key error happens in
                    # the absence of an error code -> everything fine, we pass
                    try:
                        raise ConnectionError(f"{r['errcode']}: {r['error']}")
                    except KeyError:
                        pass
                    device_id = r['device_id']
                    self.async_client.user_id, user_id = (r['user_id'],
                                                          r['user_id'])
            if self.creds.username == split_mxid(user_id)[0]:
                # save full MXID
                self.creds.username = user_id
            elif user_id != self.creds.username:
                raise ValueError(
                    f"Given Matrix ID (username) '{user_id}' does not match the access token. "
                    "This error prevents you from accidentally using the wrong account. "
                    "Resolve this by providing the correct username with your credentials, "
                    f"or reset your session by deleting {self.creds._session_stored_file}"
                    #f"{' and ' + self.config.store_path if self.config.encryption_enabled else ''}."
                )
            if device_id != self.creds.device_id:
                if client_config.encryption_enabled:
                    if self.creds.device_id is not None:
                        raise ValueError(
                            f"Given device ID (session ID) '{device_id}' does not match the access token. "
                            "This is critical, because it may break your verification status unintentionally. "
                            "Fix this by providing the correct credentials matching the stored session "
                            f"{self.creds._session_stored_file}.")
                    else:
                        info(
                            "First run with access token. "
                            "Saving device ID (session ID)...")
                        self.creds.device_id, self.async_client.device_id = (device_id, device_id)
                        self.creds.session_write_file()
                else:
                    info(
                        "Loaded device ID (session ID) does not match the access token. "
                        "Recovering automatically...")
                    self.creds.device_id, self.async_client.device_id = (device_id, device_id)
                    self.creds.session_write_file()

            if client_config.encryption_enabled:
                self.async_client.load_store()

        else:
            if self.creds.password:
                resp = await self.async_client.login(
                    password=self.creds.password,
                    device_name=self.creds.device_name)

            elif self.creds.login_token:
                resp = await self.async_client.login(
                    token=self.creds.login_token,
                    device_name=self.creds.device_name)

            else:
                raise ValueError(
                    "Can't log in: Missing access token, password, or login token"
                )

            if isinstance(resp, nio.responses.LoginError):
                raise Exception(resp)

            self.creds.device_id = resp.device_id
            self.creds.access_token = resp.access_token

        if self.async_client.should_upload_keys:
            await self.async_client.keys_upload()

        return self.async_client

    async def _send_room(self,
                         room_id: str,
                         content: dict,
                         message_type: str = "m.room.message",
                         ignore_unverified_devices: bool = False):
        """
        Send a custom event in a Matrix room.

        Parameters
        -----------
        room_id : str
            The room id of the destination of the message.

        content : dict
            The content block of the event to be sent.

        message_type : str, optional
            The type of event to send, default m.room.message.

        ignore_unverified_devices : bool, optional
            Whether to ignore that devices are not verified and send the
            message to them regardless on a per-message basis.
        """

        if self.async_client is None:
            raise Exception("AsyncClient is None!")

        try:
            res = await self.async_client.room_send(
                room_id=room_id,
                message_type=message_type,
                content=content,
                ignore_unverified_devices=ignore_unverified_devices)
            if isinstance(res, RoomSendResponse):
                res = await self.async_client.room_get_event(res.room_id, res.event_id)
                if isinstance(res, RoomGetEventResponse):
                    return res.event
        except OlmUnverifiedDeviceError:
            # print(str(e))
            error(
                "Message could not be sent. "
                "Set ignore_unverified_devices = True to allow sending to unverified devices."
            )
            error("Automatically blacklisting the following devices:")
            for user in self.async_client.rooms[room_id].users:
                if self.async_client.olm is None: break
                unverified: List[str] = list()
                for device_id, device in self.async_client.olm.device_store[
                    user].items():
                    if not (self.async_client.olm.is_device_verified(device) or
                            self.async_client.olm.is_device_blacklisted(device)
                    ):
                        self.async_client.olm.blacklist_device(device)
                        unverified.append(device_id)
                if len(unverified) > 0:
                    info(f"\tUser {user}: {', '.join(unverified)}")

            res = await self.async_client.room_send(
                room_id=room_id,
                message_type=message_type,
                content=content,
                ignore_unverified_devices=ignore_unverified_devices)
            if isinstance(res, RoomSendResponse):
                res = await self.async_client.room_get_event(res.room_id, res.event_id)
                if isinstance(res, RoomGetEventResponse):
                    return res.event

    async def __send(self, room_id: str, body: str | File,
                     use_html: bool, reply_to: str="", edit_id: str="",
                     mentions: list[str]=list()):
        if isinstance(body, str):
            if use_html: 
                return await self.send_markdown(room_id, body,
                                         reply_to=reply_to,
                                         edit_id=edit_id,
                                         mentions=mentions)
            else: 
                return await self.send_text(room_id, body,
                                     reply_to=reply_to,
                                     edit_id=edit_id,
                                     mentions=mentions)
        elif isinstance(body, File):
            return await self.send_file(room_id, body.path, reply_to=reply_to, edit_id=edit_id)

    def _add_relations(self, content: dict, reply_to: str, edit_id: str) -> dict:
        """
        Add edit or reply info to content dict
        """
        if edit_id != "":
            content['m.new_content'] = content.copy()
            content['m.relates_to'] = {
                "rel_type" : "m.replace",
                "event_id" : edit_id
            }
        elif reply_to != "":
            content['m.relates_to'] = {
                "m.in_reply_to" : {
                    "event_id" : reply_to
                }
            }
        return content

    def _add_mentions(self, content: dict, mentions: list[str]) -> dict:
        """
        Add mentions to content dict
        """
        if len(mentions) == 0: return content
        content['m.mentions'] = {
            'user_ids' : mentions
        }
        formatted_body: str = content['body']
        for user_id in mentions:
            username, _ = user_id.split(':')
            usernick = username[1:]

            entries = [user_id, username, usernick]
            position = 0
            for entry in entries:
                cur_pos = formatted_body.find(entry, position)
                if cur_pos == -1: continue
                position = cur_pos

                href = f'<a href=\"https://matrix.to/#/{user_id}\">{entry}</a>'
                formatted_body = formatted_body.replace(entry, href)
                position += len(href) 

        content['format'] = 'org.matrix.custom.html'
        content['formatted_body'] = formatted_body

        return content

    async def delete(self, room_id: str, event_id: str, reason: str | None=None):
        if self.async_client is None:
            raise Exception("AsyncClient is None!")
        return await self.async_client.room_redact(room_id, event_id, reason)

    async def ban(self, room_id: str, user_id: str, reason: str | None=None):
        """
        Ban user in room
        """
        if self.async_client is None:
            raise Exception("AsyncClient is None!")
        return await self.async_client.room_ban(room_id, user_id, reason)

    async def unban(self, room_id: str, user_id: str):
        """
        Unban user in room
        """
        if self.async_client is None:
            raise Exception("AsyncClient is None!")
        return await self.async_client.room_unban(room_id, user_id)

    async def kick(self, room_id: str, user_id: str, reason: str | None=None):
        """
        Kick user from room
        """
        if self.async_client is None:
            raise Exception("AsyncClient is None!")
        return await self.async_client.room_kick(room_id, user_id, reason)

    async def send(self, room_id: str, body: str | File,
                   use_html: bool=False, mentions: list[str]=list()):
        """
        Send text or file to room

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        return await self.__send(room_id, body, use_html, mentions=mentions)

    async def reply(self, room_id: str, body: str | File,
                    reply_to: str, use_html: bool=False,
                    mentions: list[str]=list()):
        """
        Reply message with text or file

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        return await self.__send(room_id, body, use_html,
                          reply_to=reply_to,
                          mentions=mentions)

    async def edit(self, room_id: str, body: str | File,
                   edit_id: str, use_html: bool=False,
                   mentions: list[str]=list()):
        """
        Edit message with text or file

        Parameters:
        -------------
        body: str | mxbt.types.File
            Text of message or File object to send
        use_html: bool, optional
            Use html formatting or not
        """
        return await self.__send(room_id, body, use_html,
                          edit_id=edit_id,
                          mentions=mentions) 

    async def send_text(self, room_id: str, body: str,
                        msgtype: str="m.text",
                        reply_to: str="", edit_id: str="",
                        mentions: list[str]=list()) -> tuple[MatrixRoom, RoomMessageText] | None:
        if self.async_client is None:
            raise ValueError("AsyncClient is None!")

        content: dict[str, str | dict] = {
            "msgtype" : msgtype,
            "body" : body,
        }

        content = self._add_relations(
            content, reply_to, edit_id
        )

        content = self._add_mentions(content, mentions)
            
        result = await self._send_room(room_id=room_id, content=content)
        room = self.async_client.rooms[room_id]
        if isinstance(result, RoomMessageText):
            return room, result

    async def send_markdown(self, room_id: str, body: str,
                        msgtype: str="m.text",
                        reply_to: str="", edit_id: str="",
                        mentions: list[str]=list(),
                        extensions=['fenced_code', 'nl2br', 'tables']) -> tuple[MatrixRoom, RoomMessageText] | None:
        if self.async_client is None:
            raise ValueError("AsyncClient is None!")

        content: dict[str, str | dict] = {
            "msgtype" : msgtype,
            "body" : body,
            "format" : "org.matrix.custom.html",
            "formatted_body" : markdown.markdown(body, extensions=extensions)
        }
        
        content = self._add_relations(
            content, reply_to, edit_id
        )

        content = self._add_mentions(
            content, mentions
        )
            
        result = await self._send_room(room_id=room_id, content=content)
        room = self.async_client.rooms[room_id]
        if isinstance(result, RoomMessageText):
            return room, result

    async def send_reaction(self, room_id: str, event_id: str, key: str) -> Event | None:
        return await self._send_room(
            room_id=room_id,
            content={
                "m.relates_to": {
                    "event_id": event_id,
                    "key": key,
                    "rel_type": "m.annotation"
                }
            },
            message_type="m.reaction"
        )

    async def send_file(
            self, room_id: str,
            filepath: str,
            reply_to: str="",
            edit_id: str="") -> tuple[MatrixRoom, RoomMessageImage | RoomMessageVideo | RoomMessageFile] | None:
        if self.async_client is None:
            raise ValueError("AsyncClient is None!")

        file = File(filepath)
        content = await file.upload(self.async_client)
        if content is None: return

        content = self._add_relations(
            content, reply_to, edit_id
        )

        try:
            res = await self._send_room(room_id, content)
            room = self.async_client.rooms[room_id]
            if isinstance(res, (RoomMessageImage, RoomMessageVideo, RoomMessageFile)):
                return room, res
        except:
            error("Failed to send file.")

 
