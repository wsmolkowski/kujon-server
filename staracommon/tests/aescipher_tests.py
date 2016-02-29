import unittest

from staracommon.AESCipher import AESCipher
from staracommon import constants
from staracommon.usosutils.usosinstances import USOSINSTANCES

USOSES_DECRYP_KEYS = [constants.CONSUMER_KEY, constants.CONSUMER_SECRET]


class AESCipherTest(unittest.TestCase):

    def testAESCipher(self):
        # assume
        aes = AESCipher()

        usos = USOSINSTANCES[0]

        # when
        response = aes.encrypt_dictionary(usos, USOSES_DECRYP_KEYS)

        # then
        for k in USOSES_DECRYP_KEYS:
            decrypted_value = aes.decrypt(response[k])
            self.assertEquals(usos[k], decrypted_value)
