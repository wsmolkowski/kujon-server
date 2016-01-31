import logging

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
            logging.warn("Cleaning collection: {0}".format(collection))
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

    def get_user(self, user_id):
        return self.__db.users.find_one({"_id": user_id})

    def get_users_info(self, user_id):
        return self.__db.users_info.find_one({"user_id": user_id})

    def update_users_info(self, record_id, users_info):
        return self.__db.users_info.update({"_id": record_id }, users_info)

    def insert(self, collection, document):
        return self.__db[collection].insert(document)

    def get_user_terms(self, user_id):
        terms = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        return terms

    def get_user_courses(self, user_id):
        courses = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})

        for term_data in data['course_editions'].values():
            for term in term_data:
                if term['course_id'] not in courses:
                    courses.append(term['course_id'])
        return courses

    def get_user_terms_and_courses(self, user_id):
        result = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})
        for term_data in data['course_editions'].values():
            for term in term_data:
                tc = term[constants.TERM_ID], term[constants.COURSE_ID]
                if tc not in result:
                    result.append(tc)
        return result

    def get_suggested_friends(self, user_id):
        for data in self.get_user_terms_and_courses(user_id):
            term_id, course_id = str(data[0]), str(data[1])
            print term_id, course_id

