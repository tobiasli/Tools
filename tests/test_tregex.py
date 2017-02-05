"""
Tests copied and structured from https://github.com/tobiasli/Tools
"""

import unittest
import sys
import os
import time

from hydrology_toolbox.text_tools import tregex

FIND_TEST_CASES = [
        ('nisse \w+ \d fjell','nisse fjes 3 fjell'),
        ('(?P<bogus_named_capture>nisse) \w+ \d fjell','nisse fjes 3 fjell'),
        ('(?i)(nisse) \w+ \d fjell','Nisse FJES 3 fjell'),
        ]
FIND_TEST_CASES_TYPES = [str, dict, tuple]

GROUP_TEST_CASES = [
        ('(nisse) (\w+) (\d) (fjell)','nisse fjes 3 fjell', ('nisse', 'fjes', '3', 'fjell')),
        ]

SEARCH_LIST = ['Stavern', 'Larvik', 'Sandefjord', 'Tønsberg', 'Åsgårdstrand', 'Horten', 'Holmestrand']
SEARCH_MAPPING = {'strand': ['Holmestrand', 'Åsgårdstrand', 'Stavern'], 'naberg': ['Tønsberg'], 'larv': ['Larvik']}


class TestTregexModule(unittest.TestCase):
    def test_tregex_match(self):
        for pattern, candidate in FIND_TEST_CASES:
            self.assertTrue(tregex.match(pattern, candidate), candidate)

    def test_tregex_group(self):
        for pattern, candidate, response in GROUP_TEST_CASES:
            self.assertTrue(tregex.group(pattern, candidate), response)

    def test_tregex_smart(self):
        for case, instance in zip(FIND_TEST_CASES, FIND_TEST_CASES_TYPES):
            self.assertTrue(isinstance(tregex.smart(case[0], case[1])[0], instance))

    def test_tregex_find(self):
        for search, match in SEARCH_MAPPING.items():
            result = tregex.find(search, SEARCH_LIST)

            self.assertTrue(len(result) > 0)
            self.assertTrue(result[0] in match)

        result = tregex.find_best('larvik', SEARCH_LIST, score_cutoff=1)
        self.assertTrue(result in SEARCH_LIST)

if __name__ == '__main__':
    unittest.main()
