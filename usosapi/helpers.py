import logging
import os
import traceback
from datetime import datetime
from functools import wraps


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
        logging.debug('file_name: {0} codeline: {1} function_name: {2} took: {3}'.format(
                os.path.basename(filename), code_line, text, execution_time))

        return actual_result

    # return our inner function which will intercept the call
    return timer
