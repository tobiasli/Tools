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
import re

sys.path = [os.path.split(os.path.split(os.path.realpath(__file__))[0])[0] + os.path.sep] + sys.path

class TestSimpletimerModule(unittest.TestCase):
    def test_SimpleTimer(self):
        import simpletimer

        timer = simpletimer.SimpleTimer()

        for i in range(100):
            time.sleep(0.001)
            self.assertTrue(isinstance(timer.time(), float))

    def test_ProgressTimer(self):
        import simpletimer

        timer = simpletimer.ProgressTimer(100,'This is a regular test')
        result_frame = 'This is a regular test: %3d%%: ETA:   0h  0m  0m'

        for i in range(100):
            time.sleep(0.001)
            try:
                self.assertTrue(re.findall('This is a regular test: %3d%%: ETA in' % i, timer.string(count=i)))
            except:
                1/0

        self.assertTrue(re.findall('This is a regular test: %3d%%: ETA in' % 20, timer.string(count=20)))

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimpletimerModule)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()