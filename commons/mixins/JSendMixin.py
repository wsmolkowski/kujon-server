# coding=UTF-8

import json
from datetime import date, time, datetime

from bson import ObjectId

from commons.constants import config
from commons.enumerators import Environment


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(config.DEFAULT_DATETIME_FORMAT)
        elif isinstance(obj, date):
            return obj.strftime(config.DEFAULT_DATE_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(config.DEFAULT_DATE_FORMAT)
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        return super(CustomEncoder, self).default(obj)


class JSendMixin(object):
    def success(self, data, cache_age=None, code=200):
        if not cache_age:
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        else:
            if self.config.ENVIRONMENT.lower() == Environment.PRODUCTION.value:
                self.set_header('Cache-Control', 'public, max-age={0}'.format(cache_age))
            else:
                self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'success', 'data': data, 'code': code})

    def fail(self, message, data=None, code=501):
        if message:
            message = str(message)

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'fail', 'message': message, 'data': data, 'code': code})

    def usos(self):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'usos',
                           'message': 'Przerwa w dostępie do USOS. Spróbuj ponownie za jakiś czas :)',
                           'code': 504,
                           'data': None
                           })

    def error(self, message, data=None, code=500):

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'error', 'message': message, 'data': data, 'code': code})

    def __write_json(self, data):
        self.set_header('Content-Type', 'application/json; charset={0}'.format(config.ENCODING))
        self.write(json.dumps(data, sort_keys=True, indent=4, cls=CustomEncoder, ensure_ascii=False))
        self.finish()
