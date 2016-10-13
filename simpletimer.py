﻿# -*- coding: utf-8 -*-
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

import datetime
import time
import math
import warnings

class ProgressTimer(object):
    def __init__(self,total_count,message = '', sample_size = None):
        '''
        Class for printing percentage progress and completion time estimates.

        '''

        if sample_size and sample_size/total_count > 0.7:
            warnings.warn('Progress timer sample_size is 0.7 if total item count. Revize for speed.')

        self.total_count = total_count
        self.message = message
        self.time_start = time.clock()

        if not sample_size:
            sample_size = total_count

        self.sample_size = sample_size
        self.time_sample = []

        self.count = 0

    def __str__(self):
        return self.string()

    def start(self):
        self.time_start = time.clock()

    def calculate_sample(self):
        self.count += 1
        current_time = time.clock()

        # Keep the current time for samples up to the sample size:
        if len(self.time_sample) < self.sample_size:
            self.time_sample += [current_time]
        else:
            self.time_sample.pop(0)
            self.time_sample += [current_time]

        time_sample = self.time_sample[-1] - self.time_sample[0]
        time_past = current_time - self.time_start
        time_left = time_sample*self.total_count/len(self.time_sample)-time_past    # Assumes time_past/total_time == count/total_count

        time_left = max([time_left, 0])

        hours = int(time_left/3600)
        minutes = int((time_left-hours*3600)/60)
        seconds = int(math.fmod(time_left, 60))

        percentage = self.count/self.total_count*100

        return percentage, hours, minutes, seconds

    def calculate(self, count=None):
        if not count:
            self.count += 1
        else:
            self.count = count

        current_time = time.clock()

        time_past = current_time-self.time_start
        time_left = time_past*self.total_count/self.count-time_past  # Assumes time_past/total_time == count/total_count

        time_left = max([time_left, 0])

        hours = int(time_left/3600)
        minutes = int((time_left-hours*3600)/60)
        seconds = int(math.fmod(time_left, 60))

        percentage = self.count/self.total_count*100

        return percentage, hours, minutes, seconds

    def string(self, count=None, message=''):

        if not message:
            message = self.message

        if message:
            message += ': '

        if self.sample_size != self.total_count:
            percentage, hours, minutes, seconds = self.calculate_sample(count)
        else:
            percentage, hours, minutes, seconds = self.calculate(count)

        time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        oclock = time.strftime('HH:MM')

        return '%(message)s%(percentage)3d%%: ETA in: %(hours)3dh %(minutes)2dm %(seconds)2.0ds (%(oclock)s)' % locals()

    def print(self,count = None, message = ''):
        print(self.string(count, message))


class SimpleTimer(object):
    def __init__(self, message = ''):
        '''
        Class for simple timing of calls.

        '''
        self.time_start = time.clock()
        self.message = message

    def __str__(self):
        return self.represent()

    def __repr__(self):
        return self.represent()

    def time(self):
        return time.clock()-self.time_start

    def represent(self, message = ''):
        checkpoint = self.time()

        if message:
            return '%s: %f' % (message, checkpoint)
        elif self.message:
            return '%s: %f' % (self.message, checkpoint)
        else:
            return '%f' % checkpoint

    def print(self, message = ''):
        print(self.represent(message = message))


if __name__ == '__main__':
    from tests import test_simpletimer
    test_simpletimer.run()