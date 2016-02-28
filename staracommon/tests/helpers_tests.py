import unittest

from staracommon import helpers
from staracommon import constants
from staracommon.usosutils.usosinstances import USOSINSTANCES

USOSES_DECRYP_KEYS = [constants.CONSUMER_KEY, constants.CONSUMER_SECRET]


class HelpersTest(unittest.TestCase):

    def testDecrypt(self):
        # assume

        usos = USOSINSTANCES[0]

        # when
        response = helpers.encrypt(usos, USOSES_DECRYP_KEYS)

        # then
        print response
        for k in USOSES_DECRYP_KEYS:
            print k, response[k], type(response[k])
            self.assertTrue(isinstance(response[k], str))
