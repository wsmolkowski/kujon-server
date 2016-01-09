import unittest
import motor
import settings

import mongo_utils

motor.motor_tornado.MotorClient(settings.MONGODB_URI)

class UsosupdaterTest(unittest.TestCase):

    def testShouldInsertUserToDb(self):
        # assume

        user = {

        }

        # when
        mongo_utils.insert_user(user)

        result = mongo_utils.get_user(user.user_id)

        # then
        self.assertEquals(user.user_id, result.user_id)

    '''
    def testShouldRegisterUser(self):
        # assume

        user = {
            id_mobile = None
            access_token_key = '3ShYQv8LyvgeXthKJzmJ'
            access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
            usus_id = 'UW'
        }

        user = mongo_utils.get_user(user.user_id)
        self.assertIsNone(user)

        user = mongo_utils.insert_user(user)

        mongo_user_id = mongo_utils.register_user(user)

    '''

