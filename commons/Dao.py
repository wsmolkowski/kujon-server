import logging

import pymongo
from bson.objectid import ObjectId

from AESCipher import AESCipher
from commons import settings, constants

log = logging.getLogger(__name__)


class Dao(object):
    def __init__(self, dburi=None, dbname=None):
        self.aes = AESCipher()
        if not dburi and not dbname:
            self._dburi = settings.MONGODB_URI
            self._dbname = settings.MONGODB_NAME
        else:
            self._dburi = dburi
            self._dbname = dbname

        self._db = pymongo.Connection(self._dburi)[self._dbname]
        logging.debug("Connected to MongoDB instance at uri:{0} dbname: {1}".format(self._dburi, self._dbname))

    def insert(self, collection, document):
        doc = self._db[collection].insert(document)
        logging.debug("document inserted into collection {0} with id {1}".format(collection, doc))
        return doc

    def get_usos(self, usos_id):

        usos = self._db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_ID: usos_id})
        if settings.ENCRYPT_USOSES_KEYS:
            return self.aes.decrypt_usos(usos)
        else:
            return usos

    def get_usoses(self, enabled=True):
        return self._db[constants.COLLECTION_USOSINSTANCES].find({'enabled': enabled})

    def get_user(self, user_id):
        return self._db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})

    def get_archive_user(self, user_id):
        return self._db[constants.COLLECTION_USERS_ARCHIVE].find_one({constants.USER_ID: user_id})

    def get_users_info_by_user_id(self, user_id, usos):
        """
        :param user_id: id from users table
        :param usos:
        :return:
        """
        return self._db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: ObjectId(user_id),
                                                                   constants.USOS_ID: usos[constants.USOS_ID]})

    def get_users_info(self, id, usos):
        """
        :param id: id usera z USOSa
        :param usos: usos_id
        :return: users_info record
        """
        return self._db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: id,
                                                                   constants.USOS_ID: usos[constants.USOS_ID]})

    def get_users_info_photo(self, user_id, usos_id):
        return self._db[constants.COLLECTION_PHOTOS].find_one({constants.UNIT_ID: user_id, constants.USOS_ID: usos_id})

    def get_units(self, unit_it, usos_id):
        if not isinstance(unit_it, int):
            try:
                unit_it = int(unit_it)
            except ValueError:
                raise Exception('Provided unit_it {0} is not integer'.format(unit_it))

        return self._db[constants.COLLECTION_COURSES_UNITS].find_one(
            {constants.UNIT_ID: unit_it, constants.USOS_ID: usos_id})

    def get_group(self, course_id, usos_id):
        if not isinstance(course_id, int):
            try:
                course_id = int(course_id)
            except ValueError:
                raise Exception('Provided course_id {0} is not integer'.format(course_id))

        return self._db[constants.COLLECTION_GROUPS].find_one(
            {constants.GROUP_ID: course_id, constants.USOS_ID: usos_id})

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

    def get_usos_course_edition(self, usos_id):
        return self._db[constants.COLLECTION_COURSE_EDITION].find(
            {constants.USOS_ID: usos_id})

    def get_courses_editions(self, user_id, usos_id):
        return self._db[constants.COLLECTION_COURSES_EDITIONS].find_one(
            {constants.USOS_ID: usos_id, constants.USER_ID: user_id})

    def get_courses_conducted_by_lecturers(self, usos_id):
        fields = ['course_editions_conducted']
        return self._db[constants.COLLECTION_USERS_INFO].find(
            {constants.USOS_ID: usos_id, constants.LECTURER_STATUS: constants.LECTURER_STATUS_ACTIVE}, fields)

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

    def get_courses(self, usos_id, fields):
        courses = list()
        cursor = self._db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id}, [fields])
        for elem in cursor:
            courses.append(elem[fields])
        return courses

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
            {constants.ID: user_info_id,
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
            {constants.USER_ID: ObjectId(user_id), constants.USOS_ID: usos_id})

        for term_data in data['course_editions'].values():
            for term in term_data:
                if term[constants.COURSE_ID] not in course_edition:
                    course_edition.append({constants.COURSE_ID: term[constants.COURSE_ID],
                                           constants.TERM_ID: term[constants.TERM_ID]})
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

    def courses_conducted(self, user_id):
        course_editions_conducted = self._db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: user_id}, ('course_editions_conducted',))
        if course_editions_conducted:
            return course_editions_conducted['course_editions_conducted']
        return list()

    def delete_doc(self, collection, doc_id):
        self._db[collection].remove({constants.MONGO_ID: doc_id})

    def get_users(self):
        return self._db[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True},
                    (constants.MONGO_ID, constants.USOS_ID, constants.ACCESS_TOKEN_KEY, constants.ACCESS_TOKEN_SECRET))

    def get_time_table(self, user_id, usos_id):
        tt_doc = self._db[constants.COLLECTION_TT].find_one({constants.USER_ID: user_id, constants.USOS_ID: usos_id})
        if tt_doc:
            return tt_doc[constants.MONGO_ID]
        return False
