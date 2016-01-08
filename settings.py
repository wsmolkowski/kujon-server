VERSION = 001
PORT = 8888

DATE_FORMAT = "%d-%m-%y"
DEFAULT_SCHEDULE_PERIOD = 7

MONGODB_URI = "mongodb://dbuser1:dbpass1@ds035995.mongolab.com:35995"
MONGODB_NAME = "test-db-mongo"

USOSINSTANCES = {
    'UW': {
        'name': 'Uniwersyst Warszawski',
        'url': 'https://usosapps.uw.edu.pl/',
        'consumer_key': 'KBt6uWPWUekUzFtNTyY9',
        'consumer_secret': 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG',
        'contact': 'dsksysadm@adm.uw.edu.pl'
    },
    'PS': {
        'name': 'Politechnika Swietokrzystka',
        'url': 'https://api.usos.tu.kielce.pl/',
        'consumer_key': 'equujDB5ZLzTmPfcy2c2',
        'consumer_secret': 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA',
        'contact': 'd.walczyk@tu.kielce.pl'
    }
}

USOSTESTUSERS = {
    '1264': {
        'usos_id': 'UW',
        'access_token_key' : '3ShYQv8LyvgeXthKJzmJ',
        'access_token_secret' : 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
    },
    '15822': {
        'usos_id':'PS',
        'access_token_key' : 'uXLyCGpp5zfHPH4z4brg',
        'access_token_secret' : 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'
    }
}