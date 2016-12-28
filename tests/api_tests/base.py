# coding=utf-8

import logging

import motor.motor_tornado
from motor import MotorGridFSBucket

from api import server
from commons.AESCipher import AESCipher
from commons.constants import config
from tests.base import BaseTestClass


class AbstractApplicationTestBase(BaseTestClass):
    def get_app(self):
        application = server.get_application(self.config)

        application.settings[config.APPLICATION_DB] = self.db
        application.settings[config.APPLICATION_CONFIG] = self.config
        application.settings[config.APPLICATION_AES] = self.aes
        application.settings[config.APPLICATION_FS] = self.fs
        logging.info(self.config.DEPLOY_API)

        return application
