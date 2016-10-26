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
import shutil

sys.path = [os.path.split(os.path.split(os.path.realpath(__file__))[0])[0] + os.path.sep] + sys.path


class TestLoggerModule(unittest.TestCase):
    def test_log(self):
        import logger

        log = logger.Log(dynamicPrintToScreen=True, timestamp=True)


        for i in range(100):
            log.addMessage('Message nr %d' % i)
            log.addError('Error nr %d' % i)

        self.assertTrue(log.errorCount == 100)

        write_path = os.path.dirname(__file__)
        write_name = 'test_log'
        if os.path.exists(os.path.join(write_path, write_name)):
            os.remove(os.path.join(write_path, write_name))

        log.printLogToFile(write_path, write_name)
        os.remove(log.log_file_path)

        log.printLogToFile(write_path, write_name+'.txt', completeName=True)
        os.remove(log.log_file_path)

        log.printLogToFile(write_path, write_name + '.txt', completeName=True, errorTag=True)
        os.remove(log.log_file_path)


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLoggerModule)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()