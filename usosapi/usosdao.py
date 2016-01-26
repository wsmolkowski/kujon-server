import motor

import settings


class UsosDao:
    def __init__(self):
        self.__connectin = motor.motor_tornado.MotorClient(settings.MONGODB_URI)

        self.__db = self.__connection[settings.MONGODB_NAME]
