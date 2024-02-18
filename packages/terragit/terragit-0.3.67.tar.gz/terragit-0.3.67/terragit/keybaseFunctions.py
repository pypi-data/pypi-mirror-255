import requests


class KeybaseFunctions:
    def __init__(self, ):
        self.headers = {'Content-Type': 'application/json'}

    def check_keybase_username_existance(self, username):
        url = "https://keybase.io/_/api/1.0/user/lookup.json?usernames=" + username
        return requests.get(url, headers=self.headers).json()



