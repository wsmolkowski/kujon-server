import unittest

from commons.AESCipher import AESCipher
from commons.usosutils.usosinstances import USOSINSTANCES


class AESCipherTest(unittest.TestCase):

    def testAESCipher(self):
        # assume
        aes = AESCipher()

        usos = USOSINSTANCES[0]

        # when
        encrypted = aes.encrypt_usos(usos)

        # then
        decrypted = aes.decrypt_usos(encrypted)
        self.assertEquals(usos, decrypted)
