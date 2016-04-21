from bson import json_util

from commons import utils, settings, constants


class JSendMixin(object):
    '''
    http://labs.omniti.com/labs/jsend
    JSend is a specification that lays down some rules for how JSON
    responses from web servers should be formatted.
    JSend focuses on application-level (as opposed to protocol- or
    transport-level) messaging which makes it ideal for use in
    REST-style applications and APIs.
    '''

    def success(self, data, cache_age=None):
        '''
        When an API call is successful, the JSend object is used as a simple
        envelope for the results, using the data key.

        :param data:
        :return:
        '''
        if not cache_age:
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        else:
            self.set_header('Cache-Control', 'public, max-age={0}'.format(cache_age))
        self.__write_json({'status': 'success', 'data': data})

    def fail(self, message):
        '''
        There was a problem with the data submitted, or some pre-condition
        of the API call wasn't satisfied.
        :param data:
        :return:
        '''

        if message:
            message = unicode(message, settings.UNICODE)

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json({'status': 'fail', 'message': message})

    def error(self, message, data=None, code=None):
        '''
        An error occurred in processing the request, i.e. an exception was
        thrown.
        :param message:
        :param data:
        :param code:
        :return:
        '''

        result = {'status': 'error', 'message': message}
        if data:
            result['data'] = unicode(data, settings.UNICODE)

        if code:
            result['code'] = code

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.__write_json(result)

    def __write_json(self, data):
        data = utils.serialize(data)
        if settings.DEVELOPMENT:
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

        self.set_header('Content-Type', 'application/json; charset={0}'.format(constants.ENCODING))
        self.write(json_util.dumps(data))
        self.finish()
