import logging
import os
import traceback
from datetime import datetime
from functools import wraps
from base64 import b64encode, b64decode
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

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
    aes = AESCipher("HASLO!!!")
    for key, value in dictionary.items():
        if key not in keys:
            result[key] = value
        else:
            result[key] = b64encode(aes.encrypt(value))
    return result


def decrypt(value):
    aes = AESCipher("HASLO!!!")
    return aes.decrypt(b64decode(value))