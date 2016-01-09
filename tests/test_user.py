from model import User

USOSTESTUSERS = {
    '1264': {
        'usos_id': 'UW',
        'access_token_key' : '3ShYQv8LyvgeXthKJzmJ',
        'access_token_secret' : 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
    },
    '15822': {
        'usos_id': 'PS',
        'access_token_key': 'uXLyCGpp5zfHPH4z4brg',
        'access_token_secret': 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'
    }
}

class UsersForTests:
    userfsfortests = {}

    def __init__(self):
        usoses = {}
        for key in USOSTESTUSERS:
            poz = USOSTESTUSERS[key]
            self.userfsfortests[key] = User(key, poz['usos_id'], poz['access_token_key'], poz['access_token_secret'])

    def getrandombyusosid(self,usos_id):
        for user in self.userfsfortests:
            if self.userfsfortests[user].usos_id == usos_id:
                return self.userfsfortests[user]
