# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''-------------------------------------------------------------------------------
 Name:          trineParser
 Purpose:       Rutine for å hente ut oppskrifter fra Trines Matblogg og spytte
                de ut som en yaml-fil.

 Author:      Tobias Litherland

 Created:     01.04.2015
 Copyright:   (c) Tobias Litherland 2015
-------------------------------------------------------------------------------'''

import urllib2
import tregex

path = r'http://trinesmatblogg.no/2012/09/11/verdens-beste-fiskesuppe-versjon-2-0/'

req = urllib2.Request(path)
a = urllib2.urlopen(req)
text = a.read()

oppskrift = {}

#Navn:
navn = tregex.group('<title>.*?; (?P<title>.*?)</title>',text)
if navn:
    oppskrift['navn'] = navn[0][0].decode('utf-8')
else:
    oppskrift['navn'] = ''

#Kategorier:
kategorier = tregex.find('categories.*?</span>',text)
if kategorier:
    oppskrift['kategorier'] = [a[0].decode('utf-8') for a in tregex.smart('<a href.*?>(.*?)</a>',kategorier[0])]
else:
    oppskrift['kategorier'] = []

#Tid:
tid = tregex.smart('(?P<minutter>\d+) min|(?P<timer>\d+[\.,]\d+) time',text)

if tid:
    sumTid = 0
    for t in tid:
        if t['minutter']:
            sumTid += float(t['minutter'])
        elif t['timer']:
            sumTid += float(t['timer'].replace(',','.'))*60
    tid = sumTid
else:
    tid = None
oppskrift['tid'] = tid

#Oppskrift:
oppskrift['oppskrift'] = path

#Antall personer:
personer = tregex.smart('(?P<porsjoner>\d+) porsjoner|(?P<personer>\d+) pers',text)
if personer:
    personer = personer[0]
    if personer['porsjoner']:
        personer = float(personer['porsjoner'])/2.0
    elif personer['personer']:
        personer = float(personer['personer'])
else:
    personer = None

oppskrift['antall personer i oppskrift'] = personer

#Ingredeinser:
ingredienser = tregex.group('(?:<li>([^<>]+)</li>.*?)',text)
if ingredienser:
    oppskrift['ingredienser'] = [a[0].decode('utf-8') for a in ingredienser]
else:
    oppskrift['ingredienser'] = []



#Formatér output:
if not oppskrift['antall personer i oppskrift']:
    personerFormat = ''
else:
    if int(oppskrift['antall personer i oppskrift']) == oppskrift['antall personer i oppskrift']:
        personerFormat = '%(antall personer i oppskrift)d'
    else:
        personerFormat = '%(antall personer i oppskrift)0.1f'
if not oppskrift['tid']:
    tidFormat = ''
else:
    tidFormat = '%(tid)d'


print u'        %(navn)s:' % oppskrift
print u'            kategorier: %s' % ', '.join(oppskrift['kategorier'])
print u'            tid: %s' % tidFormat % oppskrift
print u'            oppskrift: %(oppskrift)s' % oppskrift
print u'            antall personer i oppskrift: %s' % personerFormat % oppskrift
print u'            ingredienser:'
for o in oppskrift['ingredienser']:
        print u'                -   %s' % o