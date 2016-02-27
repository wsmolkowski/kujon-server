import logging
import logging

from bson import json_util

from staracommon import utils


class JSendMixin(object):
    '''
    http://labs.omniti.com/labs/jsend
    JSend is a specification that lays down some rules for how JSON
    responses from web servers should be formatted.
    JSend focuses on application-level (as opposed to protocol- or
    transport-level) messaging which makes it ideal for use in
    REST-style applications and APIs.
    '''

    def success(self, data):
        '''
        When an API call is successful, the JSend object is used as a simple
        envelope for the results, using the data key.

        :param data:
        :return:
        '''

        self.__write_json({'status': 'success', 'data': data})

    def fail(self, data):
        '''
        There was a problem with the data submitted, or some pre-condition
        of the API call wasn't satisfied.
        :param data:
        :return:
        '''

        self.__write_json({'status': 'fail', 'data': data})

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
            result['data'] = data

        if code:
            result['code'] = code

        self.__write_json(result)

    def __write_json(self, data):
        data = utils.serialize(data)
        logging.debug(data)
        self.set_header("Content-Type", "application/json")
        self.write(json_util.dumps(data))
        self.finish()
