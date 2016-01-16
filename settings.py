VERSION = 001
PROJECT_TITLE = "My title"
PORT = 8888

DATE_FORMAT = "%d-%m-%y"
DEFAULT_SCHEDULE_PERIOD = 7

MONGODB_URI = 'mongodb://dbuser1:dbpass1@ds035995.mongolab.com:35995/usos-test2'
#MONGODB_URI = 'mongodb://192.168.56.101:27017/'
MONGODB_NAME = 'usos-test2'
CLEAN_DB = False

USOSINSTANCES = [
    {
        'usos_id': 'UW',
        'name': 'Uniwersyst Warszawski',
        'url': 'https://usosapps.uw.edu.pl/',
        'consumer_key': 'KBt6uWPWUekUzFtNTyY9',
        'consumer_secret': 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG',
        'contact': 'dsksysadm@adm.uw.edu.pl'
    },
    {
        'usos_id': 'PS',
        'name': 'Politechnika Swietokrzystka',
        'url': 'https://api.usos.tu.kielce.pl/',
        'consumer_key': 'equujDB5ZLzTmPfcy2c2',
        'consumer_secret': 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA',
        'contact': 'd.walczyk@tu.kielce.pl'
    }
]
