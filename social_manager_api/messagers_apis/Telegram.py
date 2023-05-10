import asyncio
from pathlib import Path
from typing import Union, Iterable

from pyrogram import Client, enums
from pyrogram.types import Chat

from social_manager_api.exceptions import TokenError, ChatIdError


class TelegramAPI:
    def __init__(
            self,
            session_string,
            new_session_string: bool = False,
            name='social_manager',
            api_id=None,
            api_hash=None
    ):
        self.name = name
        self.api_id = api_id
        self.api_hash = api_hash

        self.app, self.session_string = self.check_session_string(
            session_string,
            new_session_string
        )

    def check_session_string(
            self,
            session_string: str,
            new_session_string: bool = False
    ) -> tuple[Client, str]:
        app = Client(
            name=self.name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_string=session_string
        )

        if new_session_string:
            try:
                with app:
                    app.get_me()
            except Exception:
                raise TokenError()

        return app, session_string

    async def find_chat_by_name_in_my_chats(self, chat_name: str) -> str:
        async with self.app:
            async for dialog in self.app.get_dialogs():
                if str(dialog.chat.title or dialog.chat.first_name) \
                        .lower() == chat_name.lower():
                    return str(dialog.chat)

    async def find_chat_by_id(self, chat_id: Union[int, str]) -> Chat:
        async with self.app:
            try:
                return await self.app.get_chat(chat_id)
            except Exception:
                raise ChatIdError()

    async def get_chat_info(
            self,
            chat_id: Union[int, str] = 'me'
    ) -> tuple[int, Union[str, None], str]:
        chat: Chat = await self.find_chat_by_id(chat_id=chat_id)

        name_list = [chat.first_name, chat.last_name, chat.title]

        chat_id = chat.id
        name = ' '.join(filter(None, name_list))
        username = chat.username

        return chat_id, name, username

    async def get_admin_chats_info(self) -> dict:
        async with self.app:
            dialogs = self.app.get_dialogs()
            me = await self.app.get_me()
            # If a channel is pinned, it appears twice in the dialogs.
            # Therefore, we save the channels in which there were already
            result = {}
            async for dialog in dialogs:
                if dialog.chat.type == enums.ChatType.CHANNEL:
                    member = await self.app.get_chat_member(dialog.chat.id, me.id)
                    status = member.status in [
                        enums.ChatMemberStatus.ADMINISTRATOR,
                        enums.ChatMemberStatus.OWNER
                    ]
                    permissions = False
                    if status:
                        permissions = (
                                member.privileges.can_post_messages and
                                member.privileges.can_edit_messages and
                                member.privileges.can_delete_messages
                        )

                    if status and permissions and not result.get(f"{dialog.chat.id}"):
                        data = {
                            "chat_id": dialog.chat.id,
                            "name": dialog.chat.title,
                            "username": dialog.chat.username

                        }

                        # save the channel in which we have already been
                        result[f"{dialog.chat.id}"] = data

            return result

    async def send_message(
            self,
            chat_id: Union[int, str],
            path: Union[str, Path],
            caption: str = "",
            parse_mode: str = "DEFAULT",
            video=None
    ) -> str:
        async with self.app:
            mode = self._get_parse_mode(parse_mode)

            if not video:
                message = await self.app.send_photo(
                    chat_id=chat_id,
                    photo=path,
                    caption=caption,
                    parse_mode=mode,
                )
            else:
                message = await self.app.send_video(
                    chat_id=chat_id,
                    video=path,
                    caption=caption,
                    parse_mode=mode,
                )
            return str(message.id)

    # The method will be used in the future
    async def edit_message(
            self,
            chat_id: Union[int, str],
            message_id: int,
            text: str,
            parse_mode: str = "DEFAULT",
    ) -> str:
        async with self.app:
            message = await self.app.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=self._get_parse_mode(parse_mode)
            )
            return str(message.id)

    async def delete_message(
            self,
            chat_id: Union[int, str],
            message_ids: Union[int, Iterable[int]],

    ) -> str:
        async with self.app:
            return str(await self.app.delete_messages(chat_id, message_ids=message_ids))

    @classmethod
    def get_tg_client(
            cls,
            session_string: str,
            new_session_string: bool = False,
    ):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tg_client = TelegramAPI(
            name='social_manager',
            session_string=session_string,
            new_session_string=new_session_string
        )

        return tg_client, loop.run_until_complete

    def _get_parse_mode(self, parse_mode) -> enums.ParseMode:
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
