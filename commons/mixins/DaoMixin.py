import logging

import motor
from bson.objectid import ObjectId
from tornado import gen

from commons import constants, settings


class DaoMixin(object):
    _db = None

    @property
    def db(self):
        if not self._db:
            self._db = motor.motor_tornado.MotorClient(settings.MONGODB_URI)
        return self._db[settings.MONGODB_NAME]

    @gen.coroutine
    def db_users_info_by_user_id(self, user_id, usos):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.USER_ID: user_id,
                                                                                 constants.USOS_ID: usos})

        raise gen.Return(user_info_doc)

    @gen.coroutine
    def db_get_user(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one({constants.MONGO_ID: user_id})
        raise gen.Return(user_doc)

    @gen.coroutine
    def db_get_usos(self, usos_id):
        usos_doc = yield self.db[constants.COLLECTION_USOSINSTANCES].find_one({constants.USOS_ID: usos_id})
        raise gen.Return(usos_doc)

    @gen.coroutine
    def db_insert(self, collection, document):
        doc = yield self.db[collection].insert(document)
        logging.debug("document {0} inserted into collection: {1}".format(doc, collection))
        raise gen.Return(doc)

    @gen.coroutine
    def db_remove(self, collection, key, key_value):
        if key == constants.MONGO_ID:
            if isinstance(key_value, str):
                key_value = ObjectId(key_value)

        result = yield self.db[collection].remove({key: key_value})
        logging.debug("removed from collection {0} with {1}".format(collection, result))
        raise gen.Return(result)

    @gen.coroutine
    def db_users_info_programmes(self, user_info_id, usos_id):
        programmes = []
        data = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: user_info_id,
                                                                        constants.USOS_ID: usos_id})
        if data:
            programmes = data['student_programmes']

        raise gen.Return(programmes)

    @gen.coroutine
    def db_programme(self, programme_id, usos_id):
        programme_doc = yield self.db[constants.COLLECTION_PROGRAMMES].find_one({constants.PROGRAMME_ID: programme_id,
                                                                                 constants.USOS_ID: usos_id})
        raise gen.Return(programme_doc)

    @gen.coroutine
    def db_courses_editions(self, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        result = list()
        data = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        if data:
            for term_data in data['course_editions'].values():
                for term in term_data:
                    tc = {constants.TERM_ID: term[constants.TERM_ID], constants.COURSE_ID:term[constants.COURSE_ID]}
                    if tc not in result:
                        result.append(tc)

        raise gen.Return(result)

    @gen.coroutine
    def db_courses(self, usos_id):
        cursor = self.db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id})
        courses = yield cursor.to_list(None)
        raise gen.Return(courses)

    @gen.coroutine
    def db_terms(self, user_id):
        terms = list()
        data = yield self.db[constants.COLLECTION_COURSES_EDITIONS].find_one({constants.USER_ID: user_id})
        for term in data['course_editions'].keys():
            if term not in terms:
                terms.append(term)
        raise gen.Return(terms)

    @gen.coroutine
    def db_course_edition(self, user_id, course_id, term_id, usos_id):
        course_edition_doc = yield self.db[constants.COLLECTION_COURSE_EDITION].find_one(
            {constants.USER_ID: user_id,
             constants.COURSE_ID: course_id,
             constants.TERM_ID: term_id,
             constants.USOS_ID: usos_id})

        raise gen.Return(course_edition_doc)

    @gen.coroutine
    def db_term(self, term_id, usos_id):
        term_doc = yield self.db[constants.COLLECTION_TERMS].find_one({constants.TERM_ID: term_id,
                                                                       constants.USOS_ID: usos_id})
        raise gen.Return(term_doc)

    @gen.coroutine
    def db_unit(self, unit_it, usos_id):
        if not isinstance(unit_it, int):
            try:
                unit_it = int(unit_it)
            except ValueError:
                raise Exception('Provided unit_it {0} is not integer'.format(unit_it))

        unit_doc = yield self.db[constants.COLLECTION_COURSES_UNITS].find_one(
            {constants.UNIT_ID: unit_it, constants.USOS_ID: usos_id})

        raise gen.Return(unit_doc)

    @gen.coroutine
    def db_group(self, group_id, usos_id):
        if not isinstance(group_id, int):
            try:
                course_id = int(group_id)
            except ValueError:
                raise Exception('Provided group_id {0} is not integer'.format(course_id))

        group_doc = yield self.db[constants.COLLECTION_GROUPS].find_one(
            {constants.GROUP_ID: course_id, constants.USOS_ID: usos_id})

        raise gen.Return(group_doc)

    @gen.coroutine
    def db_faculties_from_courses(self, usos_id):
        cursor = self.db[constants.COLLECTION_COURSES].find({constants.USOS_ID: usos_id}, (constants.FACULTY_ID,))

        result = []
        cursor_list = yield cursor.to_list(None)
        for faculty in cursor_list:
            try:
                faculty_id = int(faculty[constants.FACULTY_ID])
            except Exception, ex:
                logging.exception(ex)

            if faculty_id not in result:
                result.append(faculty_id)

        raise gen.Return(result)

    @gen.coroutine
    def db_faculty(self, fac_id, usos_id):
        faculty_doc = yield self.db[constants.COLLECTION_FACULTIES].find_one({constants.FACULTY_ID: fac_id,
                                                                              constants.USOS_ID: usos_id})

        raise gen.Return(faculty_doc)

    @gen.coroutine
    def db_users(self):
        cursor = self.db[constants.COLLECTION_USERS].find({constants.USOS_PAIRED: True},
                                                          (constants.MONGO_ID,
                                                           constants.USOS_ID,
                                                           constants.ACCESS_TOKEN_KEY,
                                                           constants.ACCESS_TOKEN_SECRET))

        users = yield cursor.to_list(None)
        raise gen.Return(users)

    @gen.coroutine
    def db_courses_conducted(self, user_id):
        course_editions_conducted = yield self.db[constants.COLLECTION_USERS_INFO].find_one(
            {constants.USER_ID: user_id}, ('course_editions_conducted',))

        if course_editions_conducted and 'course_editions_conducted' in course_editions_conducted:
            raise gen.Return(course_editions_conducted['course_editions_conducted'])

        raise gen.Return([])

    @gen.coroutine
    def db_users_info(self, id, usos_id):
        user_info_doc = yield self.db[constants.COLLECTION_USERS_INFO].find_one({constants.ID: id,
                                                                                 constants.USOS_ID: usos_id})
        raise gen.Return(user_info_doc)

    @gen.coroutine
    def db_archive_user(self, user_id):
        user_archive_doc = yield self.db[constants.COLLECTION_USERS_ARCHIVE].find_one(
            {constants.USER_ID: user_id, constants.USOS_PAIRED: True})

        raise gen.Return(user_archive_doc)

    @gen.coroutine
    def db_usoses(self, enabled=True):
        cursor = self.db[constants.COLLECTION_USOSINSTANCES].find({'enabled': enabled})
        usoses = yield cursor.to_list(None)
        raise gen.Return(usoses)
