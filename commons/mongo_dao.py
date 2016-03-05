import logging

import pymongo
from bson.objectid import ObjectId

from AESCipher import AESCipher
from commons import settings, constants


class Dao:
    def __init__(self, dburi=None, dbname=None):
        self.aes = AESCipher()
        if not dburi:
            self._dburi = settings.MONGODB_URI
        else:
            self._dburi = dburi

        if not dbname:
            self._dbname = settings.MONGODB_NAME
        else:
            self._dbname = dbname

        logging.debug("Connecting do MongoDB instance at uri:{0} dbname: {1}".format(self._dburi, self._dbname))
        self._db = pymongo.Connection(self._dburi)[self._dbname]

    def drop_collection(self, collection):
        logging.warn("Cleaning collection: {0}".format(collection))
        self._db.drop_collection(collection)

    def drop_collections(self):
        for collection in self._db.collection_names():
            if 'system' in collection:
                continue
            self.drop_collection(collection)

    def find_usos(self, usos_id):
        return self._db.usosinstances.find_one({constants.USOS_ID: usos_id})

    def insert(self, collection, document):
        return self._db[collection].insert(document)

    def get_usos(self, usos_id):
        usos = self._db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_ID: usos_id})
        return self.aes.decrypt_usos(usos)

    def get_usoses(self):
        usoses = self._db[constants.COLLECTION_USOSINSTANCES].find()
        return self.aes.decrypt_usoses(usoses)

    def get_user(self, user_id):
        return self._db[constants.COLLECTION_USERS].find_one({"_id": user_id})

    def get_users_info(self, user_id):
        return self._db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id})

    def get_users_info_by_usos_id(self, usos_user_id, usos):
        return self._db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: usos_user_id, constants.USOS_ID: usos[
            constants.USOS_ID]})

    def get_users_info_photo(self, user_id, usos_id):
        return self._db[constants.COLLECTION_PHOTOS].find_one({constants.UNIT_ID: user_id, constants.USOS_ID: usos_id})

    def get_group(self, group_id, usos_id):
        return self._db[constants.COLLECTION_COURSES_UNITS].find_one(
            {constants.GROUP_ID: group_id, constants.USOS_ID: usos_id})

    def get_units(self, unit_it, usos_id):
        return self._db[constants.COLLECTION_COURSES_UNITS].find_one(
            {constants.UNIT_ID: unit_it, constants.USOS_ID: usos_id})

    def update(self, collection, key, key_value, document):
        return self._db[collection].update({key: key_value}, document)

    def remove(self, collection, key, key_value):
        return self._db[collection].remove({key: key_value})

    def update_courses_editions(self, record_id, courses_editions):
        return self._db[constants.COLLECTION_COURSES_EDITIONS].update({constants.USER_ID: ObjectId(record_id)},
                                                                      courses_editions)

    def get_term(self, term_id, usos_id):
        return self._db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id, constants.USOS_ID: usos_id})

    def get_courses_editions(self, course_id, term_id, usos_id):
        return self._db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.COURSE_ID: course_id, constants.TERM_ID: term_id, constants.USOS_ID: usos_id})

    def get_course_edition(self, course_id, term_id, usos_id):
        return self._db[constants.COLLECTION_COURSE_EDITION].find_one(
            {constants.COURSE_ID: course_id,
             constants.TERM_ID: term_id,
             constants.USOS_ID: usos_id})

    def get_courses_editions(self, user_id, usos_id):
        return self._db[constants.COLLECTION_COURSES_EDITIONS].find(
            {constants.USOS_ID: usos_id,
             constants.USER_ID: user_id})

    def get_faculties_from_courses(self, usos_id):
        return self._db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id}).distinct(constants.FACULTY_ID)

    def get_faculty(self, fac_id, usos_id):
        return self._db[constants.COLLECTION_FACULTIES].find_one(
            {constants.FACULTY_ID: fac_id, constants.USOS_ID: usos_id})

    def find_notexisting_courses(self, course_id, usos_id):
        return self._db[constants.COLLECTION_COURSES].find_one(
            {constants.COURSE_ID: course_id, constants.USOS_ID: usos_id})

    def get_course(self, course_id, usos_id):
        return self._db[constants.COLLECTION_COURSES].find_one(
            {constants.COURSE_ID: course_id, constants.USOS_ID: usos_id})

    def get_courses(self, courses, usos_id):
        courses_comma_separated_string = u",".join(courses).encode(constants.ENCODING).strip()
        return self._db[constants.COLLECTION_COURSES].find(
            {constants.COURSE_ID: {'$in': [courses_comma_separated_string]},
             constants.USOS_ID: usos_id})

    def get_grades(self, course_id, term_id, user_id, usos_id):
        return self._db[constants.COLLECTION_GRADES].find_one(
            {constants.COURSE_ID: course_id, constants.TERM_ID: term_id, constants.USER_ID: user_id,
             constants.USOS_ID: usos_id})

    def get_user_terms(self, user_id):
        terms = list()
        data = self._db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        return terms

    def get_programme(self, programme_id, usos_id):
        return self._db[constants.COLLECTION_PROGRAMMES].find_one(
            {constants.PROGRAMME_ID: programme_id,
             constants.USOS_ID: usos_id})

    def get_users_info_programmes(self, user_info_id, usos_id):
        programmes = []
        data = self._db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_INFO_ID: user_info_id,
             constants.USOS_ID: usos_id})
        if data:
            programmes = data['student_programmes']

        return programmes

    def get_user_tt(self, user_id, usos_id, given_date):

        tt = self._db[constants.COLLECTION_TT].find_one(
            {constants.USER_ID: ObjectId(user_id),
             constants.USOS_ID: usos_id,
             constants.TT_STARTDATE: str(given_date)})
        return tt

    def get_user_courses(self, user_id, usos_id):
        course_edition = list()
        data = self._db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(user_id),
             constants.USOS_ID: usos_id})

        for term_data in data['course_editions'].values():
            for term in term_data:
                if term[constants.COURSE_ID] not in course_edition:
                    course_edition.append({constants.COURSE_ID: term[constants.COURSE_ID], constants.TERM_ID: term[
                        constants.TERM_ID]})
        return course_edition

    def get_user_courses_editions(self, user_id):
        result = list()
        data = self._db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USER_ID: ObjectId(user_id)})
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
        return self._db[collection].count()

