# coding=UTF-8

import json
from datetime import date, time, datetime

from bson import ObjectId

from commons import constants
from commons.enumerators import Environment


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(constants.DEFAULT_DATETIME_FORMAT)
        elif isinstance(obj, date):
            return obj.strftime(constants.DEFAULT_DATE_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(constants.DEFAULT_DATE_FORMAT)
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        return super(CustomEncoder, self).default(obj)


class JSendMixin(object):
    def success(self, data, cache_age=None):
        if not cache_age:
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        else:
            if self.config.ENVIRONMENT.lower() == Environment.PRODUCTION.value:
                self.set_header('Cache-Control', 'public, max-age={0}'.format(cache_age))
            else:
                self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'success', 'data': data})

    def fail(self, message, code=501):
        if message:
            message = message

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'fail', 'message': message, 'code': code})

    def usos(self):
        result = {'status': 'usos',
                  'message': 'Przerwa w dostępie do USOS. Spróbuj ponownie za jakiś czas :)',
                  'code': 504
                  }
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json(result)

    def error(self, message, data=None, code=None):

        result = {'status': 'error', 'message': message}
        if data:
            result['data'] = data

        if code:
            result['code'] = code

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json(result)

    def __write_json(self, data):
        self.set_header('Content-Type', 'application/json; charset={0}'.format(constants.ENCODING))
        self.write(json.dumps(data, sort_keys=True, indent=4, cls=CustomEncoder))
        self.finish()
