# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        tregex
# Purpose:     Wrapper that makes my everyday use of regex much smoother.
#
# Author:      Tobias Litherland
#
# Created:     10.04.2015
# Copyright:   (c) Tobias Litherland 2015
#-------------------------------------------------------------------------------
import re
import difflib

defaultFlag = re.UNICODE | re.DOTALL
namedGroupDetection = '(\(\?P<\w+>)'
namedGroupReferenceDetection = '\(\?\(\w+\)'

def match(pattern,string,output = 'smart',flags = defaultFlag):
    #Returns the named groups from a pattern match directly, isted of going
    #through the regular parsing.
    r = re.compile(pattern,flags)
    match = [found for found in r.finditer(string)]
    if match:
        returnList = []

        if output == 'smart':
            if match[0].groupdict():
                output = 'name'
            elif match[0].groups():
                output = 'group'
            else:
                output = ''

        if not output:
            for m in match:
                returnList += [m.group()]
        elif output == 'name':
            for m in match:
                returnList += [m.groupdict()]
        elif output == 'group':
            for m in match:
                returnList += [m.groups()]
        else:
            raise Exception('Unknown value for argument "output".')

        return returnList
    else:
        return []

def name(pattern,string,flags = defaultFlag):
    return match(pattern,string,output = 'name',flags = flags)

def find(pattern,string,flags = defaultFlag):
    #Only return strings matching pattern, not considering any grouping. Will
    #remove any named groups from pattern before compiling.
    pattern = re.sub(namedGroupDetection,'(',pattern) #Remove named groups.
    pattern = re.sub(namedGroupReferenceDetection,'(',pattern) #Remove named groups.
    return match(pattern,string,output = '',flags = flags)

def group(pattern,string,flags = defaultFlag):
    #Only return strings matching groups. Will remove any named groups from
    #pattern before compiling.

    pattern = re.sub(namedGroupDetection,'(',pattern) #Remove named groups.
    return match(pattern,string,output = 'group',flags = flags)

def smart(pattern,string,flags = defaultFlag):
    return match(pattern,string,output = 'smart',flags = flags)

def similarity(string1,string2):
    #Returns a score based on the degree of match between to strings:
    return difflib.SequenceMatcher(None,string1,string2).ratio()

if __name__ == '__main__':
    tallForm = '(?:(?P<teller>\d+)/(?P<nevner>\d+)|(?P<tall>\d+(?:[\.,]\d+)?))'
    tallForm2 = '(?:(\d+)/(\d+)|(\d+(?:[\.,]\d+)?))'
    print(name(tallForm,'1/4  5   5.4'))
    print(find(tallForm2,'1/4  5   5.4'))
    print(find(tallForm,'1/4  5   5.4'))
    print(group(tallForm,'1/4  5   5.4'))
    print(smart(tallForm2,'1/4  5   5.4'))