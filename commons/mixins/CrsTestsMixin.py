# coding=UTF-8

import logging

from tornado import gen

from commons import constants
from commons.mixins.DaoMixin import DaoMixin
from commons.mixins.UsosMixin import UsosMixin


class CrsTestsMixin(DaoMixin, UsosMixin):
    def do_refresh(self):
        return False

    @gen.coroutine
    def api_crstests(self):
        pipeline = {constants.USER_ID: self.get_current_user()[constants.MONGO_ID]}
        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_CRSTESTS, pipeline)

        crstests_doc = yield self.db[constants.COLLECTION_CRSTESTS].find_one(pipeline)

        if not crstests_doc:
            crstests_doc = yield self.usos_crstests_participant()
            logging.debug(crstests_doc)

            crstests_doc.pop('terms')  # no need at this point

            # rewrite response to list of crstests
            crstests = list()
            for term_id in crstests_doc['tests']:
                for crstest in crstests_doc['tests'][term_id]:
                    crstest_doc = crstests_doc['tests'][term_id][crstest]
                    crstest_doc[constants.TERM_ID] = term_id
                    crstests.append(crstest_doc)

            crstests_doc['tests'] = crstests

            yield self.db_insert(constants.COLLECTION_CRSTESTS, crstests_doc)

        raise gen.Return(crstests_doc)

    @gen.coroutine
    def api_crstests_grades(self, node_id):
        pipeline = {constants.NODE_ID: node_id, constants.USOS_ID: self.get_current_user()[constants.USOS_ID]}

        if self.do_refresh():
            yield self.db_remove(constants.COLLECTION_CRSTESTS_GRADES, pipeline)

        crstests_doc = yield self.db[constants.COLLECTION_CRSTESTS_GRADES].find_one(pipeline)

        if not crstests_doc:
            crstests_doc = yield self.usos_crstests_user_grade(node_id)

            yield self.db_insert(constants.COLLECTION_CRSTESTS_GRADES, crstests_doc)

        raise gen.Return(crstests_doc)
