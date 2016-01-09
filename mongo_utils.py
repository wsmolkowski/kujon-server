import settings
import pymongo

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

        for key, values in USOSINSTANCES.items():
           doc = self.__db.usosinstances.find_one({'usosinstance': key})
           if not doc:
               insert = {'usosinstance': key, 'usosdata': values}
               self.__db.usosinstances.insert(insert)

