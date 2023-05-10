import time
from typing import Union

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import transaction
from rest_framework.exceptions import APIException

from social_manager_api.exceptions import AccountTypeError, TokenError, AccountDataError, PostCreateError
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
        chat_id, name, username = None, None, None
        account_type = validated_data.get("type", None)
        token = validated_data.get("token", None)
        verification_code = validated_data.get("verification_code", None)

        if account_type == AccountType.TELEGRAM:
            if not token:
                raise TokenError()

            tg_client, run = TelegramAPI.get_tg_client(token, True)
            chat_id, name, username = run(tg_client.get_chat_info())

        if account_type == AccountType.INSTAGRAM:
            instagram_username = validated_data.get("username")
            instagram_password = validated_data.get("password")

            if not instagram_password and not instagram_password:
                raise AccountDataError()

            client = InstagramAPI(
                username=instagram_username,
                password=instagram_password,
                verification_code=verification_code
            )

            chat_id, name, username = client.get_me()
            validated_data['token'] = client.session_id

        if account_type == AccountType.TIK_TOK:
            pass

        if not chat_id:
            raise AccountTypeError()

        chat = Chat.objects.filter(chat_id=chat_id).first()
        if chat:
            account = chat.account
            account.token = validated_data['token']
            account.name = name

            chat.name = name
            chat.username = username

            account.save()
            chat.save()

        else:
            account = Account.objects.create(
                name=name,
                type=validated_data['type'],
                token=validated_data['token'],
                user_id=user_id
            )

            Chat.objects.create(
                name=name,
                username=username,
                chat_id=chat_id,
                account_id=account.pk,
                user_id=user_id
            )

        return account


class ChatService:
    def update_chats(
            self,
            session_id: str,
            account_id: int,
            user_id: int,
            account_type: AccountType = AccountType.TELEGRAM,
    ):
        chats = {}
        if account_type == AccountType.TELEGRAM:
            tg_client, run = TelegramAPI.get_tg_client(session_id)
            tg_chat_id, tg_name, tg_username = run(tg_client.get_chat_info())
            chats.update(run(tg_client.get_admin_chats_info()))
            self._update_chats_dict(
                chats=chats,
                chat_id=tg_chat_id,
                name=tg_name,
                username=tg_username
            )

        if account_type == AccountType.INSTAGRAM:
            client = InstagramAPI(session_id=session_id)
            inst_chat_id, inst_name, inst_username = client.get_me()
            self._update_chats_dict(
                chats=chats,
                chat_id=inst_chat_id,
                name=inst_name,
                username=inst_username
            )

        if chats:
            Chat.objects.filter(
                account_id=account_id,
                user_id=user_id,
                account__type=account_type
            ).exclude(
                chat_id__in=chats.keys(),
            ).delete()

            update_instances = []
            create_instances = []
            for chat_id, data in chats.items():
                instance: Chat = Chat.objects.filter(chat_id=chat_id).first()

                if not instance:
                    instance = Chat(
                        **data,
                        user_id=user_id,
                        account_id=account_id
                    )
                    create_instances.append(instance)
                else:
                    instance.name = data['name']
                    instance.username = data['username']
                    update_instances.append(instance)

            Chat.objects.bulk_create(create_instances)
            Chat.objects.bulk_update(update_instances, ['name', 'username'])

    def _update_chats_dict(
            self,
            chats: dict,
            chat_id: str,
            name: str,
            username: str
    ) -> None:
        data = {
            "chat_id": chat_id,
            "name": name,
            "username": username
        }
        chats[f"{chat_id}"] = data


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

        caption = self._format_text(validated_data)

        photo = validated_data.get('photo', None)
        video = validated_data.get('video', None)
        file: TemporaryUploadedFile = photo or video

        for chat in chats:
            session_id = chat.account.token
            message_id = None

            if chat.account.type == AccountType.TELEGRAM:
                chat_id = chat.chat_id
                parse_mode = validated_data.get('parse_mode', "DEFAULT")

                try:
                    tg_client, run = TelegramAPI.get_tg_client(session_id)
                    message_id = run(
                        tg_client.send_message(
                            chat_id=chat_id,
                            path=file.temporary_file_path(),
                            caption=caption,
                            parse_mode=parse_mode,
                            video=video
                        )
                    )
                except Exception as e:
                    raise APIException(e.args)

            if chat.account.type == AccountType.INSTAGRAM:
                try:
                    inst_client = InstagramAPI(session_id=session_id)
                    message_id = inst_client.create_post(
                        path=file.temporary_file_path(),
                        caption=caption,
                        video=video
                    )
                except Exception as e:
                    raise APIException(e.args)

            if message_id:
                message = Message.objects.create(
                    message_id=message_id,
                    account=chat.account,
                    chat_id=chat.id,
                    user_id=user_id
                )
                validated_data['message_ids'] += [message]
                validated_data['accounts'] += [chat.account]
                validated_data['chats'] += [chat]

        post = self._save_in_db(validated_data=validated_data, user_id=user_id)

        return post

    @transaction.atomic()
    def edit_post(self, validated_data, messages):
        for message in messages:
            session_id = message.account.token

            caption = self._format_text(validated_data)

            if message.account.type == AccountType.TELEGRAM:
                chat_id = message.chat.chat_id
                parse_mode = validated_data.get('parse_mode', "DEFAULT")

                try:
                    tg_client, run = TelegramAPI.get_tg_client(session_id)
                    run(
                        tg_client.edit_message(
                            chat_id=chat_id,
                            message_id=int(message.message_id),
                            text=caption,
                            parse_mode=parse_mode,
                        )
                    )
                except Exception as e:
                    raise APIException(e.args)

            if message.account.type == AccountType.INSTAGRAM:
                try:
                    inst_client = InstagramAPI(session_id=session_id)
                    inst_client.edit_post(
                        message_id=message.message_id,
                        caption=caption
                    )
                except Exception as e:
                    raise APIException(e.args)

    @transaction.atomic()
    def delete_post(
            self,
            messages,
    ):
        for message in messages:
            session_id = message.account.token

            if message.account.type == AccountType.TELEGRAM:
                try:
                    tg_client, run = TelegramAPI.get_tg_client(session_id)
                    run(
                        tg_client.delete_message(
                            chat_id=message.chat.chat_id,
                            message_ids=int(message.message_id)
                        )
                    )
                except Exception as e:
                    raise APIException(e.args)

            if message.account.type == AccountType.INSTAGRAM:
                try:
                    inst_client = InstagramAPI(session_id=session_id)
                    inst_client.delete_post(message.message_id)
                    time.sleep(2)
                except Exception as e:
                    raise APIException(e.args)

    def _format_text(self, validated_data: dict):
        return f'{validated_data.get("title" "")}' \
               f'\n{validated_data.get("description" "")}' \
               f'\n{validated_data.get("hash_tag" "")}'

    @transaction.atomic()
    def _save_in_db(
            self,
            validated_data,
            user_id
    ) -> Union[Post, None]:

        accounts = validated_data.pop('accounts', [])
        message_ids = validated_data.pop('message_ids', [])
        chats = validated_data.pop('chats', [])

        if not message_ids:
            raise PostCreateError()

        post = Post.objects.create(**validated_data, user_id=user_id)
        post.accounts.set(accounts)
        post.message_ids.set(message_ids)
        post.chats.set(chats)

        return post
