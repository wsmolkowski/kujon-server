# coding=utf-8
import locale
import unittest
from functools import cmp_to_key


class SortTest(unittest.TestCase):
    def testSortPolishList(self):
        # assume
        list_input = ["Adamczak",
                      "Bedla",
                      "Chodorek",
                      "Gorzałczany",
                      "Grosicki",
                      "Głuszek",
                      "Janowska",
                      "Tuszyński",
                      "Wiśniewski",
                      "Zawarczyński",
                      "Łukawska",
                      "Łukawski",
                      ]

        # when
        # WATCH: pl_PL.ISO8859-2 must be installed on system

        locale.setlocale(locale.LC_COLLATE, 'pl_PL.ISO8859-2')
        result = sorted(list_input, key=cmp_to_key(locale.strcoll))

        # then
        self.assertEquals(result[-1], 'Zawarczyński')
