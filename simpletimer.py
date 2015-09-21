# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#-------------------------------------------------------------------------------
# Name:        simpletimer
# Purpose:     A simple timer for for-loops.
#
# Author:      u34386
#
# Created:     18.09.2015
# Copyright:   (c) u34386 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import time
import math

class ProgressTimer(object):
    def __init__(self,total_count = None,message = ''):
        '''
        Class for printing percentage progress and completion time estimates.

        '''
        self.message = message
        self.total_count = total_count
        self.time_start = time.clock()
        self.count = 0

    def __str__(self):
        return self.string()

    def string(self,count = None, message = ''):

        if not message and self.message:
            message = self.message

        if not count:
            self.count += 1

        current_time = time.clock()

        time_past = current_time-self.time_start
        time_left = time_past*self.total_count/self.count-time_past    # Assumes time_past/total_time == count/total_count

        hours = int(time_left/3600)
        minutes = int((time_left-hours*3600)/60)
        seconds = int(math.fmod(time_left,60))
        try:
            percentage = (time_past/time_left)*100
        except ZeroDivisionError:
            percentage = 0

        return '%(message)s: %(percentage)3d%%: ETA: %(hours)3dh %(minutes)2dm %(seconds)2.0dm' % locals()

    def print(self,count = None, message = ''):
        print(string(self,count, message))


class SimpleTimer(object):
    def __init__(self):
        '''
        Class for simple timing of calls.

        '''
        self.time_start = time.clock()

    def print(self):
        print(time.clock()-self.time_start)