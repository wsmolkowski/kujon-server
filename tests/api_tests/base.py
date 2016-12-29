# coding=utf-8

from api import server
from tests.base import BaseTestClass


class AbstractApplicationTestBase(BaseTestClass):
    def get_app(self):
        return server.get_application(self.config)
