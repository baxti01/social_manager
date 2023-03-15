class InstagramAPI:
    API_VERSION = 'v16.0'
    BASE_URL = 'https://graph.facebook.com/'

    def __init__(self, name, api_id, api_secret, access_token):
        self.name = name
        self.api_id = api_id
        self.api_hash = api_secret
        self.access_token = access_token

    def create_message(self):
        pass

    def edit_message(self):
        pass

    def delete_message(self):
        pass
