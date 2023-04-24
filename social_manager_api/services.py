import asyncio

from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException

from social_manager_api.exceptions import AccountTypeError, UniqueError
from social_manager_api.messagers_apis.Instagram import InstagramAPI
from social_manager_api.messagers_apis.Telegram import TelegramAPI
from social_manager_api.models import Post, AccountType, Message, Account, Chat


class AccountService:
    @classmethod
    @transaction.atomic()
    def create_account(
            cls,
            validated_data: dict,
            user_id: int,
    ) -> Account:
        account = Account(
            **validated_data,
            user_id=user_id
        )

        chat_id, name, username = None, None, None

        if account.type == AccountType.TELEGRAM:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            run = loop.run_until_complete

            tg_api = TelegramAPI(
                session_string=account.token,
                new_session_string=True
            )

            chat_id, name, username = run(tg_api.get_chat_info())

        if account.type == AccountType.INSTAGRAM:
            chat_id, name, username = InstagramAPI.get_ig_id_with_name(
                token=account.token
            )

        if account.type == AccountType.TIK_TOK:
            pass

        if not chat_id:
            raise AccountTypeError()

        try:
            account.save()
        except IntegrityError:
            raise UniqueError(
                detail=f'Account name "{account.name}" already is exist.'
            )

        Chat.objects.create(
            name=name,
            username=username,
            chat_id=chat_id,
            account_id=account.pk,
            user_id=user_id
        )

        return account

    @classmethod
    def update_account(
            cls,
            validated_data: dict,
            user_id: int
    ) -> Account:
        pass


class PostService:
    @transaction.atomic()
    def create_post(
            self,
            validated_data: dict,
            user_id,
    ):
        chats = validated_data.pop('chats', [])

        validated_data['chats'] = []
        validated_data['message_ids'] = []
        validated_data['accounts'] = []

        for chat in chats:
            if chat.account.type == AccountType.TELEGRAM:
                data = validated_data.copy()
                data['chat_id'] = chat.chat_id

                session_string = chat.account.token

                try:
                    message_id = self._get_loop().run_until_complete(
                        TelegramAPI(name='social_manager', session_string=session_string)
                        .send_message(data)
                    )
                    message = Message.objects.create(
                        message_id=message_id,
                        account=chat.account,
                        chat_id=chat.id,
                        user_id=user_id
                    )
                    validated_data['message_ids'] += [message]
                    validated_data['accounts'] += [chat.account]
                    validated_data['chats'] += [chat]
                except Exception as e:
                    raise APIException(e.args)

            if chat.account.type == AccountType.INSTAGRAM:
                pass

        post = self._save_in_db(validated_data=validated_data, user_id=user_id)

        return post

    def edit_post(self, validated_data, messages):
        for message in messages:
            if message.account.type == AccountType.TELEGRAM:
                data = validated_data.copy()
                data['chat_id'] = message.chat.chat_id
                data['message_id'] = message.message_id

                session_string = message.account.token

                try:
                    self._get_loop().run_until_complete(
                        TelegramAPI(
                            name='social_manager',
                            session_string=session_string
                        ).edit_message(data)
                    )
                except Exception as e:
                    raise APIException(e.args)

    def delete_post(
            self,
            messages,
    ):
        for message in messages:
            if message.account.type == AccountType.TELEGRAM:
                session_string = message.account.token

                try:
                    self._get_loop().run_until_complete(
                        TelegramAPI(name='social_manager', session_string=session_string)
                        .delete_message(
                            chat_id=message.chat.chat_id,
                            message_ids=int(message.message_id)
                        )
                    )
                except Exception as e:
                    raise APIException(e.args)
            if message.account.type == AccountType.INSTAGRAM:
                pass
            

    def _get_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    def _save_in_db(
            self,
            validated_data,
            user_id
    ):

        accounts = validated_data.pop('accounts', [])
        message_ids = validated_data.pop('message_ids', [])
        chats = validated_data.pop('chats', [])

        post = Post.objects.create(**validated_data, user_id=user_id)
        post.accounts.set(accounts)
        post.message_ids.set(message_ids)
        post.chats.set(chats)

        return post
