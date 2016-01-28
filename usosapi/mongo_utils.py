import pymongo

import constants
import settings


class Dao:
    def __init__(self):
        self.__db = pymongo.Connection(settings.MONGODB_URI)[settings.MONGODB_NAME]

    def drop_collections(self):
        for collection in self.__db.collection_names():
            if 'system' in collection:
                continue
            print 'Cleaning collection:', collection
            self.__db.drop_collection(collection)

    def prepare(self):
        if settings.CLEAN_DB:
            self.drop_collections()

        for usos in settings.USOSINSTANCES:
            doc = self.__db.usosinstances.find_one({constants.USOS_ID: usos[constants.USOS_ID]})
            if not doc:
                self.__db.usosinstances.insert(usos)

    def get_usos(self, usos_id):
        return self.__db.usosinstances.find_one({constants.USOS_ID: usos_id})

    def get_usoses(self):
        return self.__db.usosinstances.find()
