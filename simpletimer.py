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

class ProgressTimer(object):
    def __init__(self,total_count = None,message = ''):
        '''
        Class for printing percentage progress and completion time estimates.

        '''
        self.message = message
        self.total_count = total_count
        self.time_start = time.clock()
        self.count = 0

    def print(self,message = ''):

        if not message and self.message:
            message = self.message

        self.count += 1
        current_time = time.clock()

        time_past = current_time-self.time_start
        time_left = time_past*self.total_count/self.count-time_past    # Assumes time_past/total_time == count/total_count

        hours = int(time_left/3600)
        minutes = int((time_left-hours*3600)/60)
        seconds = int(math.fmod(time_left,60))
        percentage = (time_past/time_left)*100

        print('%(message)s: %(percentage)d/100: Est. Time left: %(hours)dh %(minutes)dm %(seconds)dm' % locals())
