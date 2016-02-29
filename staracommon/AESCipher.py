from base64 import b64encode, b64decode
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

import settings
import constants


class AESCipher(object):
    def __init__(self):
        self.usos_keys = [constants.CONSUMER_KEY, constants.CONSUMER_SECRET]
        self.encoding = 'utf-8'
        self.bs = 32
        self.key = hashlib.sha256(settings.COOKIE_SECRET).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(raw))

    def encrypt_usos(self, dictionary):
        for key, value in dictionary.items():
            if key not in self.usos_keys:
                continue
            else:
                dictionary[key] = self.encrypt(value)
        return dictionary

    def encrypt_usoses(self, usoses):
        result = []
        for usos in usoses:
            result.append(self.encrypt_usos(usos))
        return result

    def decrypt(self, enc):
        enc = b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode(self.encoding)

    def decrypt_usos(self, dictionary):
        for key, value in dictionary.items():
            if key not in self.usos_keys:
                continue
            else:
                dictionary[key] = self.decrypt(value)
        return dictionary

    def decrypt_usoses(self, usoses):
        result = []
        for usos in usoses:
            result.append(self.decrypt_usos(usos))
        return result

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
