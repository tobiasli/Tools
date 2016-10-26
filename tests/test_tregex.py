# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#-------------------------------------------------------------------------------
# Name:        test_units
# Purpose:      Test the components of the units module.
#
# Author:      Tobias
#
# Created:     19.10.2015
# Copyright:   (c) Tobias 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import unittest
import sys
import os
import time

sys.path = [os.path.split(os.path.split(os.path.realpath(__file__))[0])[0] + os.path.sep] + sys.path

FIND_TEST_CASES = [
        ('nisse \w+ \d fjell','nisse fjes 3 fjell'),
        ('(?P<bogus_named_capture>nisse) \w+ \d fjell','nisse fjes 3 fjell'),
        ('(?i)(nisse) \w+ \d fjell','Nisse FJES 3 fjell'),
        ]
FIND_TEST_CASES_TYPES = [str, dict, tuple]

GROUP_TEST_CASES = [
        ('(nisse) (\w+) (\d) (fjell)','nisse fjes 3 fjell', ('nisse', 'fjes', '3', 'fjell')),
        ]

class TestTregexModule(unittest.TestCase):
    def test_tregex_find(self):
        import tregex

        for pattern, candidate in FIND_TEST_CASES:
            self.assertTrue(tregex.find(pattern, candidate), candidate)

    def test_tregex_group(self):
        import tregex

        for pattern, candidate, response in GROUP_TEST_CASES:
            self.assertTrue(tregex.find(pattern, candidate), response)

    def test_tregex_smart(self):
        import tregex

        for case, type in zip(FIND_TEST_CASES, FIND_TEST_CASES_TYPES):
            self.assertTrue(isinstance(tregex.smart(case[0], case[1])[0], type))

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTregexModule)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()