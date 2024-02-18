from nio import UploadError
from enum import Enum
from PIL import Image
import aiofiles.os
import mimetypes
import filetype
import aiofiles
import os

from ..utils import error

class FileType(Enum):
    Image = 0
    Video = 1
    Other = 2

class File:

    def __init__(self, path: str) -> None:
        self.path = path
        self.mime_type = self.guess_mimetype()

        if filetype.is_image(path):
            self.filetype = FileType.Image
        elif filetype.is_video(path):
            self.filetype = FileType.Video
        else:
            self.filetype = FileType.Other

    def is_image(self) -> bool:
        return self.filetype == FileType.Image

    def is_video(self) -> bool:
        return self.filetype == FileType.Video

    def is_regular_file(self) -> bool:
        return self.filetype == FileType.Other

    def guess_mimetype(self) -> str | None:
        return mimetypes.guess_type(self.path)[0]

    async def upload(self, async_client) -> dict | None:
        """
        Upload file to Matrix server, returns base dict with file content

        Parameters:
        -------------
        async_client: nio.AsyncClient - Async Matrix client for uploading file
        """
        if self.filetype == FileType.Image:
            return await self.__upload_image(async_client)
        elif self.filetype == FileType.Video:
            return await self.__upload_video(async_client)
        elif self.filetype == FileType.Other:
            return await self.__upload_regular_file(async_client)

    async def __upload_to_server(self, async_client, file_stat) -> tuple:
        async with aiofiles.open(self.path, "r+b") as file:
            resp, maybe_keys = await async_client.upload(
                file,
                content_type=self.mime_type,
                filename=os.path.basename(self.path),
                filesize=file_stat.st_size)
        return resp, maybe_keys

    async def __upload_regular_file(self, async_client) -> dict | None:
        file_stat = await aiofiles.os.stat(self.path)
        resp, _ = await self.__upload_to_server(async_client, file_stat)
        if isinstance(resp, UploadError):
            error(f"Failed Upload Response: {resp}")
            return

        filename = os.path.basename(self.path)
        return {
            "body" : filename,
            "filename" : filename,
            "info" : {
                "mimetype" : self.mime_type,
                "size" : file_stat.st_size
            },
            "msgtype" : "m.file",
            "url" : resp.content_uri
        }

    async def __upload_image(self, async_client) -> dict | None:
        image = Image.open(self.path)
        (width, height) = image.size

        file_stat = await aiofiles.os.stat(self.path)
        resp, _ = await self.__upload_to_server(async_client, file_stat)
        if isinstance(resp, UploadError):
            error(f"Failed Upload Response: {resp}")
            return 

        return {
            "body": os.path.basename(self.path),
            "info": {
                "size": file_stat.st_size,
                "mimetype": self.mime_type,
                "thumbnail_info": None,
                "w": width,
                "h": height,
                "thumbnail_url": None
            },
            "msgtype": "m.image",
            "url": resp.content_uri
        }

    async def __upload_video(self, async_client) -> dict | None:
        file_stat = await aiofiles.os.stat(self.path)
        resp, _ = await self.__upload_to_server(async_client, file_stat)
        if isinstance(resp, UploadError):
            error(f"Failed Upload Response: {resp}")
            return

        return {
            "body": os.path.basename(self.path),
            "info": {
                "size": file_stat.st_size,
                "mimetype": self.mime_type,
                "thumbnail_info": None
            },
            "msgtype": "m.video",
            "url": resp.content_uri
        }

