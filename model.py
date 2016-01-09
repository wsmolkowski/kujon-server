
class User:
    name = None
    user_id = None
    usos_id = None
    access_token_key = None
    access_token_secret = None

    def __init__(self, user_id, usos_id, access_token_key, access_token_secret):
        self.user_id = user_id
        self.usos_id = usos_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
