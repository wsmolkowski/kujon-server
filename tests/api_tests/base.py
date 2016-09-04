# coding=utf-8

import logging

import motor.motor_tornado

from api import server
from commons import constants
from commons.AESCipher import AESCipher
from tests.base import BaseTestClass


class AbstractApplicationTestBase(BaseTestClass):
    def get_app(self):
        application = server.get_application(self.config)
        db = motor.motor_tornado.MotorClient(self.config.MONGODB_URI)[self.config.MONGODB_NAME]
        logging.info(db)
        application.settings[constants.APPLICATION_DB] = db
        application.settings[constants.APPLICATION_CONFIG] = self.config
        application.settings[constants.APPLICATION_AES] = AESCipher(self.config.AES_SECRET)

        return application
