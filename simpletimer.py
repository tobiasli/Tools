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

import datetime
import time
import math
import warnings

class ProgressTimer(object):
    def __init__(self, total_count, message='', sample_size=None):
        """Class for printing percentage progress and completion time estimates.

        total_count -- int, the total amount of iterations
        message -- str, the standard message printed at call to the ProgressTimer
        sample_size -- int, with a very large iteration set, set a fixed amount of iterations to estimate ETA over.
        """

        assert isinstance(total_count, int)
        assert isinstance(sample_size, (type(None), int))
        assert isinstance(message, str)

        if sample_size and sample_size/total_count > 0.7 and total_count > 100:
            warnings.warn('Progress timer sample_size is 0.7 if total item count. Revise for speed.')

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

    def calculate_sample(self, count):
        """Return the percentage of completion along with the hours, minutes and seconds until completion. Calculated
        based on a subset of iterations.

        Based on elapsed time compared to total number of iterations and the executed iterations:

        count/total_count = time_passed/total_time
        total_time = count/(total_count * time_passed)
        time_left = total_time - time_passed

        If count is not specified, automatically increment by 1.
        """
        assert isinstance(count, (type(None), int))
        if count is None:
            self.count += 1
        else:
            self.count = count
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
        time_left = time_sample*self.total_count/len(self.time_sample)-time_past  # Assumes time_past/total_time == count/total_count

        time_left = max([time_left, 0])

        hours = int(time_left/3600)
        minutes = int((time_left-hours*3600)/60)
        seconds = int(math.fmod(time_left, 60))

        percentage = self.count/self.total_count*100

        return percentage, hours, minutes, seconds

    def calculate(self, count=None):
        """Return the percentage of completion along with the hours, minutes and seconds until completion. Calculated
        based on all performed iterations.

        Based on elapsed time compared to total number of iterations and the executed iterations:

        count/total_count = time_passed/total_time
        total_time = count/(total_count * time_passed)
        time_left = total_time - time_passed

        If count is not passed, automatically increment by 1.
        """
        assert isinstance(count, (type(None), int))
        if count is None:
            self.count += 1
        else:
            self.count = count

        if self.count == 0:
            percentage = 0
            hours = 0
            minutes = 0
            seconds = 0
        else:
            current_time = time.clock()

            time_past = current_time-self.time_start
            time_left = time_past*self.total_count/self.count-time_past  # Assumes time_past/total_time == count/total_count

            time_left = max([time_left, 0])

            hours = int(time_left/3600)
            minutes = int((time_left-hours*3600)/60)
            seconds = int(math.fmod(time_left, 60))

            percentage = self.count/self.total_count*100

        return percentage, hours, minutes, seconds

    def string(self, message='', count=None):
        """Return the string representation of the current progress. If count if not specified, will automatically
        increment by 1."""
        assert isinstance(count, (type(None), int))
        assert isinstance(message, str)

        if not message:
            message = self.message

        if message:
            message += ': '

        if self.sample_size != self.total_count:
            percentage, hours, minutes, seconds = self.calculate_sample(count)
        else:
            percentage, hours, minutes, seconds = self.calculate(count)

        percentage = round(percentage)  # Round so decimals are not just cropped.

        time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        oclock = time.strftime('%H:%M')

        return '%(message)s%(percentage)3d%%: ETA in: %(hours)3dh %(minutes)2dm %(seconds)2.0ds (%(oclock)s)' % locals()

    def print(self, message='', count=None):
        """Print the current string representation of progress. If count is not specified, automatically increment by
        1."""
        assert isinstance(count, (type(None), int))
        assert isinstance(message, str)
        print(self.string(message, count))


class SimpleTimer(object):
    def __init__(self, message=''):
        """Class for simple timing of calls.
        message -- str, the message accompanying the elapsed time.

        """
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

    def print(self, message=''):
        print(self.represent(message=message))


if __name__ == '__main__':
    from tests import test_simpletimer
    test_simpletimer.run()