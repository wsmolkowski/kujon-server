import logging
import os
import traceback
from datetime import datetime
from functools import wraps
from Crypto.Cipher import AES
from Crypto import Random

import settings

IV = Random.new().read(AES.block_size) #Random.new().read(DES3.block_size)
CIPHER = AES.new(settings.AES_KEY, AES.MODE_CFB, IV)


def in_dictlist((key, value), my_dictlist):
    '''*args and **kwargs are the parameters that are supplied to our original function'''
    for this in my_dictlist:
        if this[key] == value:
            return this
    return {}


def log_execution_time(intercepted_function):
    @wraps(intercepted_function)
    def timer(*args, **kwargs):
        '''*args and **kwargs are the parameters that are supplied to our original function'''
        '''TODO: add settings parameter for setting on/off'''
        # get our actual function name
        stack = traceback.extract_stack()
        filename, code_line, func_name, text = stack[-2]

        # call our actual function
        # store the return of the function in a parameter

        start = datetime.now()
        actual_result = intercepted_function(*args, **kwargs)
        stop = datetime.now()

        execution_time = stop - start
        logging.debug(u'file_name: {0} codeline: {1} function_name: {2} took: {3}'.format(
            os.path.basename(filename), code_line, text, execution_time))

        return actual_result

    # return our inner function which will intercept the call
    return timer


def encrypt(dictionary, keys=[]):
    result = dict()
    for key, value in dictionary.items():
        if key not in keys:
            result[key] = value
        else:
            result[key] = CIPHER.encrypt(value)
    return result
