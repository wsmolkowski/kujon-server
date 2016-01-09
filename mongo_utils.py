import settings
import pymongo
import constants


USOSINSTANCES = [{
        constants.USOS_ID: 'UW',
        'name': 'Uniwersyst Warszawski',
        'url': 'https://usosapps.uw.edu.pl/',
        'consumer_key': 'KBt6uWPWUekUzFtNTyY9',
        'consumer_secret': 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG',
        'contact': 'dsksysadm@adm.uw.edu.pl'
    },{
        'usos_id': 'PS',
        'name': 'Politechnika Swietokrzystka',
        'url': 'https://api.usos.tu.kielce.pl/',
        'consumer_key': 'equujDB5ZLzTmPfcy2c2',
        'consumer_secret': 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA',
        'contact': 'd.walczyk@tu.kielce.pl'}
]

class Dao:
    def __init__(self):
        self.__db = pymongo.Connection(settings.MONGODB_URI)[settings.MONGODB_NAME]

    def drop_collections(self):
        for collection in self.__db.collection_names():
            if 'system' in collection:
                continue
            print 'Cleaning collection ', collection
            self.__db.drop_collection(collection)

    def prepare(self):
        if settings.CLEAN_DB:
            self.drop_collections()

        for usos in USOSINSTANCES:
           doc = self.__db.usosinstances.find_one({constants.USOS_ID: usos[constants.USOS_ID]})
           if not doc:
               self.__db.usosinstances.insert(usos)

    def get_usos(self, usos_id):
        return self.__db.usosinstances.find_one({constants.USOS_ID: usos_id})
