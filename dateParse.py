# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
Method dateParse.parse(string) returns a datetime-object for any reference to a
time that lies within string. String can detect complex dates in any string.
Examples:
    string = 'en gang på 1600-tallet'       => 1600-01-01 00:00:00
    string = 'midten av det 14. århundre'   => 1350-01-01 00:00:00
    string = 'den 14. mai 1927, kl 19:22'   => 1927-05-14 19:22:00
    string = '14.05.2012 kl 1306'           => 2012-05-14 13:06:00
    string = 'fjerde kvartal 2002'          => 2002-10-01 00:00:00


The method assumes that 2-digit years are in current century if the two digits
are lower than the current 2-digit year, while higher numbers are assumed to
be in the previous century. Examples:
    Current year = 2014
    string = 'midten av 12'                 => 2012-06-01 00:00:00
    string = '17. desember 22'              => 1922-12-17 00:00:00

(the method uses current year, and is not hardcoded to 2014)

Added functionality to parse weekdays as input. Method will interpret weekdays
and find the first upcoming dates (including today) that match the weekday name.

Written by:
    Tobias Litherland
    tobiaslland@gmail.com

History:
    07.04.2015  TL  Objectified script. Streamline logic within parser.
                    Reduced parsing time to 1/280 on simpe dates. Added history.
    01.05.2014  TL  Started groundwork.

Future improvements:
    - Token lookback to make sure the number seperators for time is consistent.
    - Fix handling of relative centuries.

'''

import re
from collections import OrderedDict
import datetime
import time as timer

class dateParse(object):

    def __init__(self):
        self.weekdays = OrderedDict([
                    ('mandag',0),
                    ('tirsdag',1),
                    ('onsdag',2),
                    ('torsdag',3),
                    ('fredag',4),
                    ('lørdag',5),
                    ('søndag',6),
                    ('man',0),
                    ('tir',1),
                    ('ons',2),
                    ('tor',3),
                    ('fre',4),
                    ('lør',5),
                    ('søn',6),
                    ('monday',0),
                    ('tuesday',1),
                    ('wednesday',2),
                    ('thursday',3),
                    ('friday',4),
                    ('saturday',5),
                    ('sunday',6),
                    ('mon',0),
                    ('tue',1),
                    ('wed',2),
                    ('th',3),
                    ('fri',4),
                    ('sat',5),
                    ('sun',6),
                    ])

        #Month variations with month number:
        self.months = OrderedDict([
                        ('januar', 1),
                        ('februar', 2),
                        ('mars', 3),
                        ('april', 4),
                        ('mai', 5),
                        ('juni', 6),
                        ('juli', 7),
                        ('august', 8),
                        ('september', 9),
                        ('oktober', 10),
                        ('november', 11),
                        ('desember', 12),
                        ('january', 1),
                        ('february', 2),
                        ('march', 3),
                        ('may', 5),
                        ('june', 6),
                        ('july', 7),
                        ('october', 10),
                        ('december', 12),
                        ('jan', 1),
                        ('feb', 2),
                        ('mar', 3),
                        ('apr', 4),
                        ('jun', 6),
                        ('jul', 7),
                        ('aug', 8),
                        ('sep', 9),
                        ('okt', 10),
                        ('nov', 11),
                        ('des', 12),
                        ('oct', 10),
                        ('dec', 12)
                        ])

        #Number of valid days in each month:
        self.days = {
                1: 31,
                2: 29,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31
                }

        #Relative position in year. Numbers are the months corresponding to the
        #start of the relative position (i.e. Q1 = 1 not 3)
        self.relativeYears = {
                    'sommer(?:en)?':6,
                    'høst(?:en)?':9,
                    'vinter(?:en)?':12,
                    'vår(?:en)?':3,
                    'første kvartal':1,
                    '1. kvartal':1,
                    'Q1':1,
                    'andre kvartal':4,
                    '2. kvartal':4,
                    'Q2':4,
                    'tredje kvartal':7,
                    '3. kvartal':7,
                    'Q3':7,
                    'fjerde kvartal':10,
                    '4. kvartal':10,
                    'Q4':10,
                    'første halvdel':1,
                    'tidlig':1,
                    'starten av':1,
                    'andre halvdel':6,
                    'midten av':6,
                    'sent':10,
                    }

        #Identification of typical century variations:
        self.centuries = [
                     '(\\d{2}00)[-\s]tallet',
                     '(\\d{2}).? århundre'
                    ]
        #Identification of various relative positions in centuries, with the
        #corresponding year:
        self.relativeCenturies = {
                        'første halvdel av(?: det)?':0,
                        'første kvartal':0,
                        'andre kvartal':25,
                        'tredje kvartal':50,
                        'fjerde kvartal':75,
                        'tidlig (?:i|på)(?: det)?':0,
                        'starten av(?: det)?':0,
                        'andre halvdel av(?: det)?':50,
                        'midten av(?: det)?':50,
                        'sent på(?: det)?':90,
                        'slutten av(?: det)?':90,
                        'begynnelsen av(?: det)?':0,
                        }

        self.day = '%(day)s'
        self.month = '%(month)s'
        self.year = '%(year)s'
        self.time = '%(time)s'

        self.weekday = '%(weekday)s'
        self.relativeYear = '%(relativeYear)s'
        self.century = '%(century)s'
        self.relativeCentury = '%(relativeCentury)s'


        #The order of what to look for. Higher complexity should come first for
        #tests to not overlap. I.e, if [year] is placed first, it will trump
        #everything.
        self.combinations = [
                     [self.day,self.month,self.year,self.time],
                     [self.year,self.month,self.day,self.time],
                     [self.time,self.day,self.month,self.year],
                     [self.time,self.year,self.month,self.day],
                     [self.day,self.month,self.year],
                     [self.year,self.month,self.day],
                     [self.day,self.month],
                     [self.month,self.day],
                     [self.weekday,self.time],
                     [self.time,self.weekday],
                     [self.weekday],
                     [self.month,self.year],
                     [self.year,self.month],
                     [self.relativeCentury,self.century],
                     [self.century,self.relativeCentury],
                     [self.relativeYear,self.year],
                     [self.year,self.relativeYear],
                     [self.century],
                     [self.year],
                     ]

        self.referenceDate = None
        self.string = ''


    def parse(self,stringIn,debugMode = False,referenceDate = None):
        '''
        (stringIn = string, debugMode = boolean/False)
        Takes any string and checks if it can find any valid dates within. Variable
        "combinations" controlls the variants that are looked for, and in what order
        they are prioritized.

        All dates and months are checked for accepted values and string is
        rechecked if values are outside acceptable bounds.

        All identifiable formats are listed below, and lists may be appended at
        will. All text identifications are regular expressions.

        '''

        string = stringIn
        match = False

        if not string:
            return []

        if not referenceDate:
            self.referenceDate = datetime.date.today()
        elif isinstance(referenceDate,str):
            self.referenceDate = self.parse(referenceDate)
        else:
            self.referenceDate = referenceDate

##        #Make sure all strings are unicode:
##        if not isinstance(string,unicode):
##            string = string.decode('utf-8')


        self.string = string

        date = []

        #Method has been rewritten to handle time as well as date.
        #Start by removing all time-of-day numbers (i.e. 14:02:37) from the string,
        #as these are difficult to handle otherwise:
        #string = re.sub(r'\d{2}:\d{2}(?::\d{2})?','',string)

        #Check for simple, pure number dates:
        dayFormat = r'(?P<day>\d{2})'
        monthFormat = r'(?P<month>\d{2})'
        yearFormat = r'(?P<year>\d{4}|\d{2})'
        simpleCombos = [[dayFormat,monthFormat,yearFormat],[yearFormat,monthFormat,dayFormat]]
        for combo in simpleCombos:
            pattern = '\D{1,2}?'.join(combo)
            r = re.compile(pattern)
            date = [found for found in r.finditer(string)]

            [match,date] = self.checkDate(date)
            if match:
               break

        #Complex date search:
        if not match:
            for combo in self.combinations:
                #Switch between months and relatives for second order unit according to which combination is in use.
                patternPart = {}

                if [True for c in combo if 'time' in c]:
                    patternPart['time'] = r'(?:(?:(?:kl)|(?:klokka)|(?:klokken))\D{1,2})?(?P<hour>\d{1,4})(?:\D(?P<minute>\d{2}))?(?:\D(?P<second>\d{2}))?'

                if [True for c in combo if 'relativeYear' in c]:
                     loopThrough = self.relativeYears
                     for Str,Num in loopThrough.items():
                        patternPart['relativeYear'] = r'(?P<month>(?i)%s)' % Str
                        patternPart['year'] = r'(?P<year>\d{4}|\d{2})'
                        [match,date] = self.checkPattern(patternPart,combo,Num)
                        if match: break

                elif [True for c in combo if 'relativeCentury' in c or 'century' in c]:
                     loopThrough = self.relativeCenturies
                     for Str,Num in loopThrough.items():
                        patternPart['century'] = r'(?P<century>(?i)%s)' % '|(?i)'.join(self.centuries)
                        patternPart['relativeCentury'] = r'(?P<relativeCentury>(?i)%s)' % '|(?i)'.join([Str])
                        [match,date] = self.checkPattern(patternPart,combo,Num,centuryCheck = True)
                        if match: break

                elif [True for c in combo if 'weekday' in c]:
                     loopThrough = self.weekdays
                     for Str,Num in loopThrough.items():
                        patternPart['weekday'] = r'(?P<weekday>(?i)%s)' % Str
                        [match,date] = self.checkPattern(patternPart,combo,Num)
                        if match: break

                else:
                    loopThrough = self.months
                    for Str,Num in loopThrough.items():
                        patternPart['day'] = r'(?P<day>\d{1,2})'
                        patternPart['month'] = r'(?P<month>(?i)%s)' % '|(?i)'.join([Str] + [r'(?:^|(?<=[^:\d]))0?' + str(Num) + r'(?:(?=[^:\d])|$)'])
                        patternPart['year'] = r'(?P<year>\d{4}|\d{2})'
                        [match,date] = self.checkPattern(patternPart,combo,Num)
                        if match: break
                if match:
                   break

        if debugMode:
           return [stringIn,combo,pattern,datetime.datetime(**date)]
        else:
            if match:
                return datetime.datetime(**date)
            else:
                return []

    def checkPattern(self,patternPart,combo,Num = 0,centuryCheck = False):
        #Run a pattern through the regular expression and return output.
        pattern = '(?:^|(?<=\D))' + '(?=[^:\d])[^:\d]{1,4}?(?<=[^:\d])'.join(combo) % patternPart  + '(?:(?=\D)|$)'

        r = re.compile(pattern)
        date = [found for found in r.finditer(self.string)]

        #Check integrity of match:
        [match,date] = self.checkDate(date,Num,centuryCheck)

        return [match,date]

    def checkDate(self,date,Num = 0,centuryCheck = False):
           #Takes an input date dictionary and check and massages the content until
           #until is fails or creates a passable date.
           match = True
           if not date:
               match = False
               return [match,date]
           elif not isinstance(date,dict):
                date = date[0].groupdict()
                for part in date:
                    if not part:
                       match = False
                       return[match,date]

           #Get first upcoming weekday
           if 'weekday' in date:
                if re.findall('^\d+$',date['weekday']):
                    dayOfTheWeek = int(date['weekday'])
                else:
                    dayOfTheWeek = self.weekdays[date['weekday']]
                delta = datetime.timedelta(days=1)
                i=0
                candidate = self.referenceDate+delta*i
                while not candidate.weekday() == dayOfTheWeek:
                    i+=1
                    candidate = self.referenceDate+delta*i
                date['day'] = str(candidate.day)
                date['month'] = str(candidate.month)
                date['year'] = str(candidate.year)

           #Check if days are found:
           if not 'day' in date:
              date['day'] = 1
           elif not date['day']:
                date['day'] = 1
           else:
                date['day'] = int(date['day'])

           #Get month number:
           if not 'month' in date:
              date['month'] = 1
           elif not date['month']:
                date['month'] = 1
           elif not re.findall(r'\d+',date['month']):
                date['month'] = Num
           else:
                date['month'] = int(date['month'])

           if date['month'] > 12:
                match = False
                return[match,date]

           #Check if days are valid amount:
           try: days[date['month']]
           except:
                  pass
           if date['day'] > self.days[date['month']]: #Days higher than monthly maximum.
                  match = False
                  return [match,date]

            #If only month/day is found, find first upcoming date matching the day/month combo.
           if not 'year' in date:
                today = datetime.datetime.today()
                currentYear = today.year
                if today.month > date['month']:
                    currentYear += 1
                elif today.month == date['month']:
                    if today.day > date['day']:
                        currentYear += 1
                date['year'] = str(currentYear) #Convert to string to not have to hamper code further down.

           if 'relativeCentury' in date:
              if date['relativeCentury']:
                 date['relativeCentury'] = Num
              else: date['relativeCentury'] = 0
           else: date['relativeCentury'] = 0

           if 'century' in date:
                 excerpt = re.findall('(?:' + '|'.join(self.centuries) + ')',date['century'])
                 if re.findall('\\d{2}.? århundre',date['century']):
                    #The first "århundre" starts with year 0, so we subtract to get the actual year:
                    correctCentury = -100
                 else:
                      correctCentury = 0
                 for d in excerpt[0]: #There should only be one hit here, we just don't know which.
                     if d:
                         date['year'] = d

           #Check two-number years and centuries;
           if len(date['year']) == 2 and centuryCheck:
              date['year'] = int(date['year'])*100 + date['relativeCentury'] + correctCentury

           elif len(date['year']) == 4 and centuryCheck:
                date['year'] = int(date['year']) + date['relativeCentury'] + correctCentury

           elif len(date['year']) == 4:
                date['year'] = int(date['year'])

           elif len((date['year'])) == 2:
              if int(date['year']) > int(str(datetime.datetime.now().year)[-2:]): #More than current two-number year.
                 date['year'] = int(date['year']) + 1900 #Assumed last century.
              else:
                   date['year'] = int(date['year']) + 2000 #Assumed this century.

           if 'hour'in date:
             if len(date['hour']) == 4:
                date['minute'] = date['hour'][2:4]
                date['hour'] = date['hour'][0:2]
             date['hour'] = int(date['hour'])
             if date['hour'] > 24 and date['hour'] < 0: match = False

             if 'minute' in date:
                if not date['minute']:
                    date['minute'] = 0
                date['minute'] = int(date['minute'])
                if date['minute'] > 60 and date['minute'] < 0: match = False

                if 'second' in date:
                  if not date['second']:
                    date['second'] = 0
                  date['second'] = int(date['second'])
                  if date['second'] > 60 and date['second'] < 0: match = False


           for k in list(date.keys()):
            if not k in ['year','month','day','hour','minute','second']:
                del date[k]

           return [match,date]



if __name__ == '__main__':
    strings = ['14. mai 2012','14.05.2012 kl 1306','mandag 14:53','saturday']

    parser = dateParse()

    for string in strings:
        start= timer.clock()
        print(parser.parse(string))
        print('\tTime spent: %0.6f' % (timer.clock()-start))

