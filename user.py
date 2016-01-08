import settings


class User:
    name = None;
    user_id = None;
    usos_id = None;
    access_token_key = None;
    access_token_secret = None;

    def __init__(self, user_id, usos_id, access_token_key, access_token_secret):
        self.user_id = user_id
        self.usos_id = usos_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


class UsersForTests:
    userfsfortests = {}

    def __init__(self):
        usoses = {}
        for key in settings.USOSTESTUSERS:
            poz = settings.USOSTESTUSERS[key];
            self.userfsfortests[key] = User(key, poz['usos_id'], poz['access_token_key'], poz['access_token_secret'])

    def getrandombyusosid(self,usos_id):
        for user in self.userfsfortests:
            if self.userfsfortests[user].usos_id == usos_id:
                return self.userfsfortests[user]
