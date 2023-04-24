import requests

from social_manager import settings
from social_manager_api.exceptions import TokenError


class InstagramAPI:
    API_VERSION = 'v16.0'
    BASE_URL = 'https://graph.facebook.com/'
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
        pass

    def delete_message(self):
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
            f"https://graph.facebook.com/v16.0/{user_id}/accounts?"
            f"access_token={token}"
        )

        page_id = accounts.json()['data'][0]['id']

        ig_accounts = requests.get(
            f"https://graph.facebook.com/v16.0/{page_id}?"
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
            f'{cls.BASE_URL}{cls.API_VERSION}/{ig_id}/'
            f'?fields=name,username&access_token={token}'
        ).json()

        name = data.get('name', None)
        username = data.get('username', None)

        return ig_id, name, username

    def __str__(self):
        return f'{self.name}'
