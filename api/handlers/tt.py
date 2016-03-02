# coding=UTF-8

import tornado.web
from bson.objectid import ObjectId
from datetime import date, timedelta
from base import BaseHandler
from commons import constants
from commons.usosutils.usosclient import UsosClient
from commons.usosutils import usosinstances

class TTApi(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, given_date):

        parameters = yield self.get_parameters()

        #checking if date is correct
        try:
            given_date = date(int(given_date[0:4]), int(given_date[5:7]), int(given_date[8:10]))
            monday = given_date - timedelta(days=(given_date.weekday()) % 7)
            next_monday = monday + timedelta(days=7)
        except Exception, ex:
            self.error(u"Niepoprawny format daty..{0}, try: YYYY-MM-DD".format(given_date))

        # get user data
        user_doc = yield self.db[constants.COLLECTION_USERS].find_one(
                                {constants.ID: ObjectId(parameters[constants.ID])})
        # get usosdata for
        usos = next((usos for usos in usosinstances.USOSINSTANCES if usos[constants.USOS_ID] == parameters[constants.USOS_ID]), None)


        # fetch TT from mongo
        tt_doc = yield self.db[constants.COLLECTION_TT].find_one(
                                {constants.USER_ID: ObjectId(parameters[constants.ID]),
                                 constants.TT_STARTDATE: str(monday)})
        if not tt_doc:
            # fetch TT from USOS
            client = UsosClient(base_url=usos['url'],
                     consumer_key=usos['consumer_key'],
                     consumer_secret=usos['consumer_secret'],
                     access_token_key=user_doc[constants.ACCESS_TOKEN_KEY],
                     access_token_secret=user_doc[constants.ACCESS_TOKEN_SECRET])
            try:
                result = client.tt(monday)

                # TODO: obsluga type of activity. Currently there are three possible values: classgroup, classgroup2, meeting or exam..

                # insert TT to mongo
                tt = dict()
                tt[constants.USOS_ID] = parameters[constants.USOS_ID]
                tt[constants.USER_ID] = parameters[constants.ID]
                tt[constants.TT_STARTDATE] = str(monday)
                if not result:
                    result=list()
                else:
                    pass
                    # TODO: add here fetch TT for next week, that if next week will be fetech user will get data from mongo
                tt['tts'] = result
                tt_doc = yield self.db[constants.COLLECTION_TT].insert(tt)
                self.success(result)
            except Exception, ex:
                self.error(u"Bład podczas pobierania TT z USOS for {0}.".format(given_date))
        else:
            self.success(tt_doc['tts'])
