VERSION = 001
PROJECT_TITLE = "Kujon-web"
PORT = 8888
APIHOST = 'http://localhost'
DEPLOY_URL = '{0}:{1}'.format(APIHOST, PORT)

DATE_FORMAT = "%d-%m-%y"
DEFAULT_SCHEDULE_PERIOD = 7

# MONGODB_URI = 'mongodb://dbuser1:dbpass1@ds035995.mongolab.com:35995/usos-test2'
MONGODB_URI = 'mongodb://localmongoinstance/usos-test2'
MONGODB_NAME = 'usos-test2'
CLEAN_DB = False
UPDATE_DICTIONARIES = False
USOSINSTANCES = [
    {'usos': 'UW',
     'name': 'Uniwersyst Warszawski',
     'url': 'https://usosapps.uw.edu.pl/',
     'consumer_key': 'KBt6uWPWUekUzFtNTyY9',
     'consumer_secret': 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG',
     'contact': 'dsksysadm@adm.uw.edu.pl'
     },
    {'usos': 'PS',
     'name': 'Politechnika Swietokrzystka',
     'url': 'https://api.usos.tu.kielce.pl/',
     'consumer_key': 'equujDB5ZLzTmPfcy2c2',
     'consumer_secret': 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA',
     'contact': 'd.walczyk@tu.kielce.pl'
     },
    {'usos': 'PWSZ',
     'name': 'Panstwowa Wyzsza Szkola Zawodowa w Elblagu',
     'url': 'https://usosapps.pwsz.elblag.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 'l.grzybek@pwsz.elblag.pl, p.kwasniewski@pwsz.elblag.pl'
     },
     {'usos': 'AMU',
     'name': 'Uniwersytet im. Adama Mickiewicza w Poznaniu',
     'url': 'https://api.usos.tu.kielce.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 'd.walczyk@tu.kielce.pl'
     },
     {'usos': 'PB',
     'name': 'Politechnika Bialostocka',
     'url': 'https://api.uci.pb.edu.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 'r.klim@uci.pb.edu.pl'
     },
     {'usos': 'UJ',
     'name': 'Uniwersytet Jagielonski',
     'url': 'https://apps.usos.uj.edu.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 'michal.pysz@uj.edu.pl, michal.zabicki@uj.edu.pl'
     },
     {'usos': 'AWF Katowice',
     'name': 'AWF im. Jerzego Kulczyka w Katowicach',
     'url': 'https://usosapps.awf.katowice.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 's.kwiatkowski@awf.katowice.pl, b.czerwinski@awf.katowice.pl'
     },
     {'usos': 'UKW',
     'name': 'Uniwersytet Kazimierza Wielkiego w Bydgoszczy',
     'url': 'https://api.ukw.edu.pl/',
     'consumer_key': '',
     'consumer_secret': '',
     'contact': 'marekmac@ukw.edu.pl'
     },
]
CONSUMER_NAME = "usosapi"
CONSUMER_KEY = "vxSehcx4RCA8m4kgjRhY"
CONSUMER_SECRET = "T7eJsSJHSxKCshK9jrdNbNy3XCG3UXzQuYKL2VbJ"
CALLBACK_URL = "{0}:{1}/authentication/verify".format(APIHOST, PORT)
PROXY_URL = None   #
PROXY_PORT = None  #
