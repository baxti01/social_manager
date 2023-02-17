from typing import Union, Iterable

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from pyrogram import Client, enums
from pyrogram.types import InputMediaPhoto, InputMediaVideo

from social_manager import settings


class TelegramAPI:
    def __init__(self, name, api_id=None, api_hash=None, session_string=None):
        self.name = name
        self.api_id = api_id
        self.api_hash = api_hash
        # dev line
        self.session_string = session_string if session_string else settings.env('SESSION_STRING')
        # self.session_string = session_string
        self.app = Client(self.name, self.api_id, self.api_hash, session_string=self.session_string)

    async def find_chat_by_name(self, chat_name: str) -> str:
        async with self.app:
            async for dialog in self.app.get_dialogs():
                if str(dialog.chat.title or dialog.chat.first_name).lower() == chat_name.lower():
                    return str(dialog.chat)

    async def find_chat_by_id(self, chat_id: Union[int, str]) -> str:
        app = Client(self.name, self.api_id, self.api_hash)
        async with app:
            return str(await app.get_chat(chat_id))

    async def send_message(self, data: dict) -> str:
        formatted_data = self._format_data(data)
        async with self.app:
            if formatted_data.get('photo', None):
                message = await self.app.send_photo(**formatted_data)
            elif formatted_data.get('video', None):
                message = await self.app.send_video(**formatted_data)
            else:
                message = await self.app.send_message(**formatted_data)
            return str(message.id)

    async def send_photo(self, data: dict) -> str:
        formatted_data = self._format_data(data)
        async with self.app:
            message = await self.app.send_photo(**formatted_data)
            return str(message.id)

    async def send_video(self, data) -> str:
        formatted_data = self._format_data(data)
        async with self.app:
            message = await self.app.send_video(**formatted_data)
            return str(message.id)

    async def edit_message(self, validate_data) -> str:
        formatted_data = self._format_data(validate_data)
        async with self.app:
            parse_mode = formatted_data.pop('parse_mode', None)
            caption = formatted_data.pop('caption', None)

            if formatted_data.get('photo', None):
                media = InputMediaPhoto(media=formatted_data.pop('photo'), caption=caption, parse_mode=parse_mode)
                message = await self.app.edit_message_media(**formatted_data, media=media)
            elif formatted_data.get('video', None):
                media = InputMediaVideo(formatted_data.pop('video'), caption=caption, parse_mode=parse_mode)
                message = await self.app.edit_message_media(**formatted_data, media=media)
            else:
                message = await self.app.edit_message_text(**formatted_data, parse_mode=parse_mode)

            return str(message.id)

    async def delete_message(
            self,
            chat_id: Union[int, str],
            message_ids: Union[int, Iterable[int]],

    ) -> str:
        async with self.app:
            return str(await self.app.delete_messages(chat_id, message_ids=message_ids))

    def _format_data(self, data: dict):
        formatted_data = {}
        message = f'{data.pop("title" "")}' \
                  f'\n{data.pop("description" "")}' \
                  f'\n{data.pop("hash_tag" "")}'

        formatted_data['chat_id'] = data.pop('chat_id', "me")

        message_id = data.pop('message_id', None)
        if message_id:
            formatted_data['message_id'] = int(message_id)

        mode = data.pop('parse_mode', None)
        formatted_data['parse_mode'] = self._get_parse_mode(mode)

        # When sending photo or video message
        formatted_data['caption'] = message

        photo = data.pop('photo', None)
        if photo:
            if isinstance(photo, InMemoryUploadedFile):
                formatted_data['photo'] = photo.file
            elif isinstance(photo, TemporaryUploadedFile):
                formatted_data['photo'] = photo.temporary_file_path()

            return formatted_data

        video = data.pop('video', None)
        if video:
            formatted_data['video'] = video.temporary_file_path()

            return formatted_data

        # When sending text message
        formatted_data['text'] = formatted_data.pop('caption', message)

        return formatted_data

    def _get_parse_mode(self, parse_mode):
        if parse_mode == "DEFAULT" or parse_mode is None:
            return enums.ParseMode.DEFAULT

        if parse_mode == "MARKDOWN":
            return enums.ParseMode.MARKDOWN

        if parse_mode == "HTML":
            return enums.ParseMode.HTML

        if parse_mode == "DISABLED":
            return enums.ParseMode.DISABLED

        raise ValueError(f'Invalid parse mode "{parse_mode}"')

    def __str__(self):
        return f'{self.name}'
