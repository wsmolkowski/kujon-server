import logging
import os
import traceback
from datetime import datetime
from functools import wraps


def search_key_value_onlist(list_check, key, value):
    for item in list_check:
        if item[key] == value:
            return item

def in_dictlist((key, value), my_dictlist):
    """
    :param my_dictlist:
    :return:
    """
    for this in my_dictlist:
        if this[key] == value:
            return this
    return {}


def log_execution_time(intercepted_function):
    @wraps(intercepted_function)
    def timer(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        # get our actual function name
        stack = traceback.extract_stack()
        filename, code_line, func_name, text = stack[-2]

        # call our actual function
        # store the return of the function in a parameter

        start = datetime.now()
        actual_result = intercepted_function(*args, **kwargs)
        stop = datetime.now()

        execution_time = stop - start
        logging.debug(u"file_name: {0} line: {1} function_name: {2} took: {3}".format(
            os.path.basename(filename), code_line, text, execution_time))

        return actual_result

    # return our inner function which will intercept the call
    return timer
