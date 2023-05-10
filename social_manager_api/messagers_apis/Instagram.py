from pathlib import Path

import requests
from instagrapi import Client, DEFAULT_LOGGER

from social_manager import settings
from social_manager_api.exceptions import TokenError, AccountDataError


class InstagramClient(Client):

    def __init__(
            self,
            settings: dict = {},
            proxy: str = None,
            delay_range: list = None,
            logger=DEFAULT_LOGGER,
            **kwargs,
    ):
        super().__init__(settings, proxy, delay_range, logger, **kwargs)

        self.verification_code = None
        self.challenge_code_handler = self.get_code
        self.change_password_handler = self.change_password

    def get_code(self, username: str, choice=None):
        if self.verification_code:
            return int(self.verification_code)

        raise Exception("Verification code needed!")

    def change_password(self, username: str):
        raise Exception("Many login attempts have been made."
                        "Please change your account password and "
                        "try again with new password.")


class InstagramAPI:

    def __init__(
            self,
            username=None,
            password=None,
            session_id=None,
            verification_code=None
    ):
        self.username = username
        self.password = password
        self.session_id = session_id
        self.verification_code = verification_code

        try:
            if session_id:
                self.client = self.login_by_session_id(session_id)
            else:
                client = InstagramClient()
                client.verification_code = self.verification_code
                client.login(self.username, self.password)

                self.session_id = client.sessionid
                self.client = client
                self.client.dump_settings(Path(f"media/{self.session_id}.json"))
        except Exception as e:
            print(e)
            raise AccountDataError(detail=e.args)

    def login_by_session_id(self, session_id):
        client = InstagramClient()
        try:
            client.load_settings(Path(f"media/{session_id}.json"))
        except Exception as e:
            print(e.args)
            client.login_by_sessionid(sessionid=session_id)
            client.dump_settings(Path(f"media/{session_id}.json"))
            client.get_timeline_feed()

        return client

    def create_post(
            self,
            path: Path,  # JPG or MP4 file path
            caption: str = "",
            video=None
    ) -> str:
        if not video:
            post = self.client.photo_upload(
                path=path,
                caption=caption
            )
        else:
            post = self.client.video_upload(
                path=path,
                caption=caption
            )

        return post.pk

    # The method will be used in the future
    def edit_post(
            self,
            message_id: str,
            caption: str = "",
    ) -> dict:
        return self.client.media_edit(
            caption=caption,
            media_id=message_id
        )

    def delete_post(self, message_id: str) -> bool:
        return self.client.media_delete(media_id=message_id)

    def get_me(self) -> tuple[str, str, str]:
        user = self.client.user_info(str(self.client.user_id))
        return user.pk, user.full_name, user.username


class InstagramAPIGraph:
    API_VERSION = 'v16.0'
    BASE_URL = 'https://graph.facebook.com'
    DEBUG_URL = 'https://graph.facebook.com/debug_token?' \
                'input_token={input_token}&access_token={access_token}'

    def __init__(self, name, access_token, api_version=None):
        self.name = name
        self.access_token = access_token
        self.api_version = api_version if api_version else self.API_VERSION

    def create_message(
            self,
            data: dict
    ):
        pass

    def edit_message(self):
        # API GRAPH unsupported this methods
        pass

    def delete_message(self):
        # API GRAPH unsupported this methods
        pass

    @classmethod
    def check_token(
            cls,
            input_token: str,
            access_token: str = settings.env('SOCIAL_AUTH_FACEBOOK_TOKEN')
    ) -> dict:
        response = requests.get(
            cls.DEBUG_URL.format(
                input_token=input_token,
                access_token=access_token,
            )
        )

        data = response.json().get('data', None)

        if response.status_code == 200:
            error = data.get('error', None)
        else:
            error = response.json()

        if error:
            raise TokenError(
                detail=error.get('message', None)
            )

        return data

    @classmethod
    def get_ig_id(cls, token: str) -> str:
        data = cls.check_token(input_token=token)
        user_id = data.get('user_id', 'me')

        accounts = requests.get(
            f"{cls.BASE_URL}/{cls.API_VERSION}/{user_id}/accounts?"
            f"access_token={token}"
        )

        page_id = accounts.json()['data'][0]['id']

        ig_accounts = requests.get(
            f"{cls.BASE_URL}/{cls.API_VERSION}/{page_id}?"
            "fields=instagram_business_account&"
            f"access_token={token}"
        )

        ig_id = ig_accounts.json()['instagram_business_account']['id']

        return ig_id

    @classmethod
    def get_ig_id_with_name(cls, token) -> tuple[str, str, str]:
        ig_id = cls.get_ig_id(token)
        print(ig_id)
        data = requests.get(
            f'{cls.BASE_URL}/{cls.API_VERSION}/{ig_id}/'
            f'?fields=name,username&access_token={token}'
        ).json()

        name = data.get('name', None)
        username = data.get('username', None)

        return ig_id, name, username

    def __str__(self):
        return f'{self.name}'
