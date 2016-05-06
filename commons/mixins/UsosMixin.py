from datetime import datetime

from tornado import gen

from commons import constants
from commons.usosutils.usosclient import UsosClient


class UsosMixin(object):
    @gen.coroutine
    def usos_client(self):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])

        usos_client = UsosClient(usos_doc[constants.USOS_URL], usos_doc[constants.CONSUMER_KEY],
                                 usos_doc[constants.CONSUMER_SECRET],
                                 self.user_doc[constants.ACCESS_TOKEN_KEY],
                                 self.user_doc[constants.ACCESS_TOKEN_SECRET])

        raise gen.Return(usos_client)

    @gen.coroutine
    def usos_course(self, course):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.course(course)
        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        yield self.insert(constants.COLLECTION_COURSES, result)

        raise gen.Return(result)

    @gen.coroutine
    def usos_course_edition(self, course_id, term_id):
        usos_doc = yield self.get_usos(constants.USOS_ID, self.user_doc[constants.USOS_ID])
        client = yield self.usos_client()
        create_time = datetime.now()

        result = client.course_edition(course_id, term_id)

        result[constants.USOS_ID] = usos_doc[constants.USOS_ID]
        result[constants.CREATED_TIME] = create_time
        result[constants.UPDATE_TIME] = create_time

        yield self.insert(constants.COLLECTION_COURSE_EDITION, result)

        raise gen.Return(result)
