# coding=utf-8

from cryptography.fernet import Fernet

from commons import constants


class AESCipher(object):
    def __init__(self, aes_secret):
        self.usos_keys = [constants.CONSUMER_KEY, constants.CONSUMER_SECRET]
        self.encoding = constants.ENCODING
        # print(Fernet.generate_key())
        self.fernet = Fernet(aes_secret)

    def encrypt(self, raw):
        return self.fernet.encrypt(raw.encode(self.encoding))

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
        return self.fernet.decrypt(enc)

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
