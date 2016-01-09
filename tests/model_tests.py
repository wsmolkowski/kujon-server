from model import User
import constants

USOSTESTUSERS = {
    '1264': {
        constants.USOS_ID: 'UW',
        constants.ACCESS_TOKEN_KEY: '3ShYQv8LyvgeXthKJzmJ',
        constants.ACCESS_TOKEN_SECRET: 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
    },
    '15822': {
        constants.USOS_ID: 'PS',
        constants.ACCESS_TOKEN_KEY: 'uXLyCGpp5zfHPH4z4brg',
        constants.ACCESS_TOKEN_SECRET: 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'
    }
}

class UsersForTests:
    userfsfortests = {}

    def __init__(self):
        usoses = {}
        for key in USOSTESTUSERS:
            poz = USOSTESTUSERS[key]
            self.userfsfortests[key] = User(key, poz[constants.USOS_ID], poz[constants.ACCESS_TOKEN_KEY], poz[constants.ACCESS_TOKEN_SECRET])

    def getrandombyusosid(self,usos_id):
        for user in self.userfsfortests:
            if self.userfsfortests[user].usos_id == usos_id:
                return self.userfsfortests[user]
