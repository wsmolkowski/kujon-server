# coding=UTF-8

from datetime import date, timedelta

import tornado.web
import tornado.gen
from bson.objectid import ObjectId

from base import BaseHandler
from commons import constants
from commons.usosutils.usosclient import UsosClient


class TTApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, given_date):

        parameters = yield self.get_parameters()
        if not parameters:
            return

        # checking if date is correct
        try:
            given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
            # next_monday = monday + timedelta(days=7)
        except Exception:
            self.error("Niepoprawny format daty: %r.", given_date)
            return

        # get user data
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
            {constants.MONGO_ID: ObjectId(parameters[constants.MONGO_ID])})
        # get usosdata for
        usos = yield self.get_usos(constants.USOS_ID, parameters[constants.USOS_ID])

        # fetch TT from mongo
        tt_doc = yield self.db[constants.COLLECTION_TT].find_one(
            {constants.USER_ID: ObjectId(parameters[constants.MONGO_ID]),
             constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            # fetch TT from USOS
            client = UsosClient(base_url=usos[constants.USOS_URL],
                                consumer_key=usos[constants.CONSUMER_KEY],
                                consumer_secret=usos[constants.CONSUMER_SECRET],
                                access_token_key=user_doc[constants.ACCESS_TOKEN_KEY],
                                access_token_secret=user_doc[constants.ACCESS_TOKEN_SECRET])
            try:
                result = client.time_table(monday)

                # insert TT to mongo
                tt_doc = dict()
                tt_doc[constants.USOS_ID] = parameters[constants.USOS_ID]
                tt_doc[constants.USER_ID] = parameters[constants.MONGO_ID]
                tt_doc[constants.TT_STARTDATE] = str(monday)
                if not result:
                    result = list()
                tt_doc['tts'] = result
                yield self.db[constants.COLLECTION_TT].insert(tt_doc)
            except Exception:
                self.error("Błąd podczas pobierania TT z USOS for {0}.".format(given_date))
                return

        # remove english names
        for t in tt_doc['tts']:
            t['name'] = t['name']['pl']
            t['course_name'] = t['course_name']['pl']
            t['building_name'] = t['building_name']['pl']
            if t['type'] == 'classgroup':
                t['type'] = 'zajęcia'
            elif t['type'] == 'exam':
                t['type'] = 'egzamin'

        self.success(tt_doc['tts'])
