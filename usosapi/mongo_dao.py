import logging

import pymongo
from bson.objectid import ObjectId

import constants
import settings


class Dao:
    def __init__(self, dburi=None, dbname=None):
        if not dburi:
            self.__dburi = settings.MONGODB_URI
        else:
            self.__dburi = dburi

        if not dbname:
            self.__dbname = settings.MONGODB_NAME
        else:
            self.__dbname = dbname

        self.__db = pymongo.Connection(self.__dburi)[self.__dbname]

    def drop_collection(self, collection):
        logging.warn("Cleaning collection: {0}".format(collection))
        self.__db.drop_collection(collection)

    def drop_collections(self):
        for collection in self.__db.collection_names():
            if 'system' in collection:
                continue
            logging.warn("Cleaning collection: {0}".format(collection))
            self.__db.drop_collection(collection)

    def find_usos(self, usos_id):
        return self.__db.usosinstances.find_one({constants.USOS_ID: usos_id})

    def insert(self, collection, document):
        return self.__db[collection].insert(document)

    def get_usos(self, usos_id):
        return self.__db.usosinstances.find_one({constants.USOS_ID: usos_id})

    def get_usoses(self):
        return self.__db.usosinstances.find()

    def get_user(self, user_id):
        return self.__db.users.find_one({"_id": user_id})

    def get_users_info(self, user_id):
        return self.__db.users_info.find_one({constants.USER_ID: user_id})

    def get_users_info_by_usos_id(self, usos_user_id, usos):
        return self.__db.users_info.find_one({constants.ID: usos_user_id, constants.USOS_ID: usos[constants.USOS_ID]})

    def get_courses_editions(self, user_id):
        return self.__db.courses_editions.find_one({constants.USER_ID: user_id})

    def get_courses_units(self, unit_id, usos_id):
        return self.__db.courses_units.find_one({constants.UNIT_ID: unit_id, constants.USOS_ID: usos_id})

    def get_group(self, group_id, usos_id):
        return self.__db.courses_units.find_one({constants.GROUP_ID: group_id, constants.USOS_ID: usos_id})

    def update(self, collection, key, key_value, document):
        return self.__db[collection].update({key: key_value}, document)

    def remove(self, collection, key, key_value):
        return self.__db[collection].remove({key: key_value})

    def update_courses_editions(self, record_id, courses_editions):
        return self.__db.courses_editions.update({constants.USER_ID: ObjectId(record_id)}, courses_editions)

    def get_term(self, term_id, usos_id):
        return self.__db.terms.find_one({constants.TERM_ID: term_id, constants.USOS_ID: usos_id})

    def get_course_edition(self, usos_id, course_id, term_id):
        return self.__db.course_edition.find_one({constants.COURSE_ID: course_id, constants.TERM_ID: term_id, constants.USOS_ID: usos_id})

    def get_grades(self, course_id, term_id, user_id):
        return self.__db.grades.find_one(
            {constants.COURSE_ID: course_id, constants.TERM_ID: term_id, constants.USER_ID: user_id})

    def get_participants(self, course_id, term_id, usos):
        return self.__db.participants.find_one(
            {constants.COURSE_ID: course_id, constants.TERM_ID: term_id, constants.USOS_ID: usos})

    def get_user_terms(self, user_id):
        terms = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        return terms

    def get_user_programmes(self, user_id):
        programmes = []
        data = self.__db[constants.COLLECTION_USERS_INFO].find_one({'user_id': ObjectId(user_id)})
        programmes = data['student_programmes']
        return programmes

    def get_user_courses(self, user_id):
        course_edition = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})

        for term_data in data['course_editions'].values():
            for term in term_data:
                if term['course_id'] not in course_edition:
                    course_edition.append({'course_id': term['course_id'], 'term_id': term['term_id']})
        return course_edition

    def get_user_courses_editions(self, user_id):
        result = []
        data = self.__db[constants.COLLECTION_COURSES_EDITIONS].find_one({'user_id': user_id})
        if data:
            for term_data in data['course_editions'].values():
                for term in term_data:
                    tc = term[constants.TERM_ID], term[constants.COURSE_ID]
                    if tc not in result:
                        result.append(tc)
            return result
        else:
            return None

    def count(self, collection):
        return self.__db[collection].count()

    def get_friends(self, user_id):
        return self.__db[constants.COLLECTION_FRIENDS].find(ObjectId(user_id))
