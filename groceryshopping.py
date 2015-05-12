# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
-------------------------------------------------------------------------------
 Name:          handleClass
 Purpose:       Parsing and logic regarding grocery and weekly many creation
                in my home.

 Author:        Tobias Litherland

 Created:       17.03.2015
 Copyright:     (c) Tobias Litherland 2015

TODO:
 -  Legge til multiplikasjon av oppskrifter: "Mammas sjokoladekake x2"
 -  Legge til håndtering av varer vi allerede har.
 -  Frigjøre strukturen fra IO. Gjøre modulen om til et rent bibliotek, og ha
    utenpåliggende wrappere som sender inn oppskrifter, ingredienser etc.
    Dette vil også involvere å koble ukeplan-håndteringa fra kokken, muligens.

Logg:
    18.04.2015  Ferdig med første versjon av Wunderlist-integrering. Bruker
                Selenium for å kommunisere med Wunderlist, så det er ikke helt
                perfekt, men det funker. Neste er automatisk pushing til epost.
    13.04.2015  Ferdig med ukemenyhåndtering. Er ikke perfekt enda, men den
                fungerer.
    12.04.2015  Ferdig med kokebok og håntering av enheter, ingredienser og
                oppskrifter.
    10.04.2015  Klasse for ingredienser, ingredienselister og oppskrifter.
                Vurderer en egen liste for den faktiske handlelisten, men
                dropper det kanskje til fordel for en ukesMeny-klasse.
                Må begynne å se på mulighet for interaksjon, i form av
                valg å bytte ut en oppskrift, og intregrering mot Wunderlist.
    08.04.2015  Laget klasse for kokebok. Har skrevet om dateParse for å
                håndtere kommende ukedager.
    31.03.2015  Kan nå lese inn oppskrifter og parse datoer fornuftig.
                Neste steg blir å finne en lur måte å håndtere
                ingrediensobjektene på.
                Må også få kokebøkene til å håndtere typen oppskrifter:
                    Om en oppskrift inneholder kjøtt, fisk eller er vegetar, og
                    om en rett inneholder pasta, poteter, ris, salat etc.
-------------------------------------------------------------------------------
'''

import os
import re
import copy
import random
import math
import difflib
from collections import OrderedDict

import yaml

import tregex
import dateParse
import wunderTob
dateParser = dateParse.dateParse()

UNIT_PREFIXES = {'k':1000,'kilo':1000,
               'h':100,'hekto':100,
               'd':0.1,'deci':0.1,
               'c':0.01,'centi':0.01,
               'm':0.001,'milli':0.001
               }
UNIT_PROPERTIES = [ #[base unit, variants, amount unit, base unit plural ending]
        [u'g',['gram'],UNIT_PREFIXES,''],
        [u'l',['liter'],UNIT_PREFIXES,''],
        [u'm',['meter'],UNIT_PREFIXES,''],
        [u'ts',['teskje','teskjeer'],{},''],
        [u'ss',['spiseskje','spiseskjeer'],{},''],
        [u'kryddermål',[],{},''],
        [u'pakke',[],{},'pakker'],
        [u'porsjon',[],{},'porsjoner'],
        [u'boks',[],{},'bokser'],
        [u'pose',[],{},'poser'],
        [u'glass',[],{},'glass'],
        ['',[],{},''] #Some groceries are unitless.
        ]

NUMBER_FORMAT = '(?:(?P<numerator>\d+)/(?P<denominator>\d+)|(?P<amount>\d+(?:[\.,]\d+)?))'

class Unit(object):
    # Class for handling a unit.
    def __init__(self,properties):
        # Construct the Unit object from a set of properties:
        self.base_unit = properties[0]
        self.variants = properties[1]
        self.unit_prefixes = properties[2]
        self.plural_of_base_unit = properties[3]
        self.pattern = self._pattern()

    def match_unit(self,unit_string):
        # Check if input string matches unit. If true, return a unit dictionary.
        output = {}
        match = tregex.smart(self.pattern,unit_string)
        if match or not unit_string and not self.base_unit:
            return match[0]
        return False

    def normalize_amount(self,unit_dictionary):
        # Return the normalized amount for this unit, based on the unit prefix.
        if unit_dictionary['numerator'] and unit_dictionary['denominator']:
            original_amount = float(unit_dictionary['numerator'])/float(unit_dictionary['denominator'])
        elif unit_dictionary['amount']:
            original_amount = float(unit_dictionary['amount'].replace(',','.'))
        else: #No amount is specified.
            original_amount = None

        if 'unit_prefix' in unit_dictionary and unit_dictionary['unit_prefix']:
            normalized_amount = original_amount*UNIT_PREFIXES[unit_dictionary['unit_prefix']]
        else:
            normalized_amount = original_amount

        return normalized_amount

    def amount_formated(self,normalized_amount):
        # Return the amount and unit as a text string, with logic for handling
        # scaling and plurals.

        mengde = ''
        mengdeEnhet = ''
        flertall = ''
        mellomrom = ''
        brok = False

        if normalized_amount:
            if self.base_unit == 'l':
                if normalized_amount < 1:
                    mengdeEnhet = 'd'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[mengdeEnhet]
                elif normalized_amount < 0.1:
                    mengdeEnhet = 'm'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[variant]
            elif self.base_unit == 'g':
                if normalized_amount >= 1000:
                    mengdeEnhet = 'k'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[mengdeEnhet]
                elif normalized_amount < 1:
                    mengdeEnhet = 'm'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[mengdeEnhet]
            elif self.base_unit == 'm':
                if normalized_amount < 1:
                    mengdeEnhet = 'c'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[mengdeEnhet]
                elif normalized_amount < 0.01:
                    mengdeEnhet = 'm'
                    normalized_amount = normalized_amount/UNIT_PREFIXES[mengdeEnhet]

            if normalized_amount < 1: #Finn potensiell brøk:
                potensielleNevnere = [2,3,4]
                for i in potensielleNevnere:
                    rest = math.fmod(normalized_amount,1/float(i))
                    if not rest:
                        brok = True
                        teller = (normalized_amount-rest)*i
                        nevner = i
                        break
                if brok:
                    mengde = '%d/%d' % (teller,nevner)
            else:
                mengde = '%0.2f' % normalized_amount
                if mengde[-3:]=='.00':
                    mengde = '%0.0f' % normalized_amount #Fjern desimaler ved heltall

        if normalized_amount <> 1 and not brok and self.plural_of_base_unit:
            unit = self.plural_of_base_unit
        else:
            unit = self.base_unit

        if self.base_unit:
            mellomrom = ' '

        mengdeTekst = '%s%s%s%s' % (mengde,mellomrom,mengdeEnhet,unit)

        return mengdeTekst

    def _pattern(self):

        pattern_parts = {
                    'unit_prefix':'(?P<unit_prefix>%s)?' % '|'.join(self.unit_prefixes),
                    'base_unit':'(?P<base_unit>%s)' % '|'.join([self.base_unit] + self.variants),
                    'plural_of_base_unit':'(?P<plural_of_base_unit>%s)?' % self.plural_of_base_unit
                    }

        no_letter_after_base_unit = u'(?:(?=\W)|(?=$))'

        pattern_combo = ['(?i)(?:(?<= )|(?<=^))%s?[ ]?' % NUMBER_FORMAT]

        if self.unit_prefixes:
            pattern_combo += ['%(unit_prefix)s']

        pattern_combo += [pattern_parts['base_unit']]

        if self.plural_of_base_unit:
            pattern_combo += ['%(plural_ending_of_base_unit)s']

        if self.base_unit:
            pattern_combo += [no_letter_after_base_unit]

        pat = ''.join(pattern_combo) % pattern_parts

        return pat

class Units(object):
    # Class for containing several units, and determining the unit of an
    # ingredient text, returning an ingredient object.

    def __init__(self,unit_properties):
        self.units = []
        for unit in unit_properties:
            self.units += [Unit(unit_properties)]

    def match_unit(self,unit_string):
        # Check what unit the string matches with, and return a dictionary
        # containing the unit object and the properties of the unit veriation.
        pass

class IngredientComponent(object):
    # A class for a single ingredient componet. Technically the same information
    # as an Ingredient, but contained in this class to simplify summing of
    # several ingredients and keeping the origin of every single ingredient when
    # working through a chain of ingredient summing.
    #
    # An Ingredient does not have to be a litteral ingredient, but can
    # absolutely anything the user needs to buy.
    #Klasse for å håndtere en enkelt ingrediens, med enhet, mengde, skalering og
    #behandling.
    def __init__(self,ingredient_string,recipe={}):

        self.amount,amount_text = self.tolkAntall(ingredient_string)
        ingredient_string = re.sub(amount_text,'',ingredient_string,1).strip()

        self.unit,unit_text = self.tolkEnhet(ingredient_string)
        ingredient_string = re.subn(unit_text,'',ingredient_string,1)[0].strip()

        self.comment,comment_text = self.tolkKommentar(ingredient_string)
        for k in comment_text:
            ingredient_string = re.sub(k,'',ingredient_string).strip()

        self.ingredient = ingredient_string
        self.recipe = recipe

    def amount(self):
        #Returnerer summen av mengden til enheten:
        amount = None
        if self.amount and self.recipe:
                amount = self.amount*self.unit.unit_prefix_factor*self.recipe.number_of_people/self.recipe.recipe_number_of_people
        elif self.amount and not self.recipe:
            amount = self.amount*self.unit.unit_prefix_factor
        else:
            amount = None #None betyr at vi trenger varen, men mengde er uviktig. Eks: Pepper, olivenolje, friske urter, etc.

        return amount

    def mengdeTekst(self):
        return self.enhet.mengdeTekst(self.mengde())

    def tolkAntall(self,ing):
        #Tolke hva som er det angitte antallet av en ingrediens.

        tallForm = '(?:(?P<teller>\d+)/(?P<nevner>\d+)|(?P<tall>\d+(?:[\.,]\d+)?))'

        tallKombo = u'^(?:ca|omtrent|minst)? ?%s(?:[ -]+%s)?' % (tallForm,tallForm)

        tall = tregex.find(tallKombo,ing)

        if tall:
            alleTall = []
            antallTekst = tall[0]
            tall = tregex.name(tallForm,antallTekst)
            for t in tall:
                if t['tall']:
                    alleTall += [float(t['tall'].replace(',','.'))]
                elif t['teller'] and t['nevner']:
                    alleTall += [float(t['teller'])/float(t['nevner'])]
                else:
                    raise Exception(u'Dårlig tallformatering i ingrediens %s' % ing)
            antall = max(alleTall)
        else:
            antall = None
            antallTekst = ''

        return [antall,antallTekst]

    def tolkEnhet(self,ing):
        #Tolke mengdeenheten til en gitt ingrediens.
        for k,v in enhetsListe.items():
            enh = v.treff(ing)
            if enh:
                enhTekst = v.treffTekst(ing)
                break
        return enh,enhTekst

    def tolkKommentar(self,ing):
        kommentarTekst = re.findall('\(.*?\)|, .*?$',ing)
        if kommentarTekst:
            tekst = [re.findall(u'\((.*?)\)|, (.*?)$',v,re.UNICODE)[0] for v in kommentarTekst]
            kommentar = []
            for t in tekst:
                kommentar += [v for v in t if v]
            kommentar = ', '.join(kommentar)
            kommentarTekst = [re.escape(k) for k in kommentarTekst]
        else:
            kommentar = ''
            kommentarTekst = ''
        return kommentar, kommentarTekst

class Ingredient(object):
    # Class for handling an ingredient. Returning unit, summing of several units
    # and plurals of units.
    # An Ingredient consists of at least one IngredientComponent. If combining
    # two ingredients with the same unit and name, the IngredientComponent lists
    # are simply combined.
    #
    # An Ingredient does not have to be a litteral ingredient, but can
    # absolutely anything the user needs to buy.
    #
    # CONTINUE WORKING HERE. FINISH WORK ON UNIT AND UNITS WHEN THE STRUCTURE OF THE INGREDIENTS IS MORE FLESHED OUT.
    pass

class GroceryList(object):
    # Class for handling a list of ingredients. Methods for combining lists, and
    # for collating the ingrediens by combining duplicates.
    pass


class Recipe(object):
    # Class for handling a recipe. A recipe has several properties and a list of
    # ingredients.
    #
    # Recipe needs to differentiate between scaling to a number of people, and
    # scaling by multiplication.
    pass

class Cookbook(object):
    # Class for handling a collection of Recipies. Contains search functions for
    # the recipies contained within.
    pass

class enhet(object):
    def __init__(self,enhetEgenskaper):
        self.grunnenhet = enhetEgenskaper[0]
        self.varianter = enhetEgenskaper[1]
        self.mengdebenevninger = enhetEgenskaper[2]
        self.flertallsending = enhetEgenskaper[3]
        self.mengdeJustering = 1

        self.form = self.lagEnhetsForm()

        pass

    def mengdeTekst(self,tallMengde):
        #Returnerer mengde og enhet som en tekststreng, men logikk angående
        #skalering ved store tall på SI-enheter, brøker og flertallsending på
        #enheter.

        mengde = ''
        mengdeEnhet = ''
        flertall = ''
        mellomrom = ''
        brok = False

        if tallMengde:
            if self.grunnenhet == 'l':
                if tallMengde < 1:
                    mengdeEnhet = 'd'
                    tallMengde = tallMengde/siMengder[mengdeEnhet]
                elif tallMengde < 0.1:
                    mengdeEnhet = 'm'
                    tallMengde = tallMengde/siMengder[variant]
            elif self.grunnenhet == 'g':
                if tallMengde >= 1000:
                    mengdeEnhet = 'k'
                    tallMengde = tallMengde/siMengder[mengdeEnhet]
                elif tallMengde < 1:
                    mengdeEnhet = 'm'
                    tallMengde = tallMengde/siMengder[mengdeEnhet]
            elif self.grunnenhet == 'm':
                if tallMengde < 1:
                    mengdeEnhet = 'c'
                    tallMengde = tallMengde/siMengder[mengdeEnhet]
                elif tallMengde < 0.01:
                    mengdeEnhet = 'm'
                    tallMengde = tallMengde/siMengder[mengdeEnhet]

            if tallMengde < 1: #Finn potensiell brøk:
                potensielleNevnere = [2,3,4]
                for i in potensielleNevnere:
                    rest = math.fmod(tallMengde,1/float(i))
                    if not rest:
                        brok = True
                        teller = (tallMengde-rest)*i
                        nevner = i
                        break
                if brok:
                    mengde = '%d/%d' % (teller,nevner)
            else:
                mengde = '%0.2f' % tallMengde
                if mengde[-3:]=='.00':
                    mengde = '%0.0f' % tallMengde #Fjern desimaler ved heltall

        if tallMengde <> 1 and not brok and self.flertallsending:
            flertall = self.flertallsending

        if self.grunnenhet:
            mellomrom = ' '

        mengdeTekst = '%s%s%s%s%s' % (mengde,mellomrom,mengdeEnhet,self.grunnenhet,flertall)

        return mengdeTekst

    def treff(self,ing):
        #Sjekk om en ingrediens passer med enheten.
        match = tregex.smart(self.form,ing)
        enhetRetur = copy.deepcopy(self)
        if match:
            match = match[0]
            if 'mengdebenevning' in match:
                if match['mengdebenevning']:
                    enhetRetur.mengdebenevning = match['mengdebenevning']
                    enhetRetur.mengdeJustering = siMengder[match['mengdebenevning']]
            return enhetRetur
        else: return []

    def treffTekst(self,ing):
        #Sjekk om en ingrediens passer med enheten.
        match = tregex.find(self.form,ing)
        if match: return match[0]
        else: return []


    def lagEnhetsForm(self):

        formMal = {
                    'mengdebenevning':'(?P<mengdebenevning>[%s])?' % ''.join(self.mengdebenevninger),
                    'grunnenhet':'(?P<grunnenhet>%s)' % '|'.join([self.grunnenhet] + self.varianter),
                    'flertallsending':'(?P<flertallsending>%s)?' % self.flertallsending
                    }

        ikkeBokstavEtterEnhet = u'(?=\W)'

        formKombo = ['(?i)(?:(?<= |\d)|(?<=^))']

        if self.mengdebenevninger:
            formKombo += ['%(mengdebenevning)s']

        formKombo += [formMal['grunnenhet']]

        if self.flertallsending:
            formKombo += ['%(flertallsending)s']

        if self.grunnenhet:
            formKombo += [ikkeBokstavEtterEnhet]

        form = ''.join(formKombo) % formMal

        return form


enhetsListe = OrderedDict()
for en in enheter:
    enhetsListe[en[0]] = enhet(en)


class oppskrift(object):
    def __init__(self,oppskriftUbehandlet):
        self.navn = oppskriftUbehandlet['navn']
        self.oppskrift = oppskriftUbehandlet['oppskrift']
        self.kategorier = self.tolkKategorier(oppskriftUbehandlet['kategorier'])
        self.personer = standardAntallPersoner #Dersom ikke annet er angitt, så skal middag beregnes
                                                    #for 2 personer.
        self.oppskriftPersoner = oppskriftUbehandlet['antall personer i oppskrift']

        self.ingredienser = ingrediensListe()
        for ing in oppskriftUbehandlet['ingredienser']:
            self.ingredienser.leggTil(ingrediens(ing,self))

    def tolkKategorier(self,kategorier):
        if kategorier:
            kategorier = kategorier.split(',')
        return kategorier

class ingrediensListe(object):
    #Klasse for håndtering av mange ingredienser.

    def __init__(self):
        self.alleIngredienser = []

    def ingredienser(self,baklengsSortering = False):
        #Returnerer en sammenstilt, alfabetisk liste av alle ingrediensene.
        return self.sammenstill(baklengsSortering)

    def ingredienserTekst(self):
        #Returnerer en enkel tekstliste over alle ingrediensene i listen.
        tekstListe = []
        for ing in self.ingredienser(baklengsSortering = True):
            if ing.mengde():
                tekstListe += [u' '.join([ing.mengdeTekst(),ing.vare])]
            else:
                tekstListe += [ing.vare]
        return tekstListe

    def komponentTekst(self):
        #Returner en enkel tekstliste over alle komponentene til hver ingrediens
        #i listen.
        tekstListe = []
        for ing in self.ingredienser(baklengsSortering = True):
            tekstListe += [ing.komponentTekst()]
        return tekstListe

    def leggTil(self,ing):
        #Legg en ingrediens til i listen. Dersom en sammenlignbar ingrediens
        #allerede finnes i listen vil den summeres. De individuelle
        #ingrediensene kan finnes i egenskapen alleIngredienser..
        if isinstance(ing,list):
            self.alleIngredienser += ing
        elif isinstance(ing,ingrediens):
            self.alleIngredienser += [ing]
        else:
            raise Exception('Metode kan kun ta imot ingrediens-objekter.')

    def sammenstill(self,baklengsSortering = False):
        #Summerer innhold på tvers av ingredienser.
        ingredienser = {}
        for ing in self.alleIngredienser:
            identifikator = ing.vare+ing.enhet.grunnenhet
            if not identifikator in ingredienser:
                ingredienser[identifikator] = ingrediensGruppe(ing)
            else:
                ingredienser[identifikator].leggTil(ing)

        ingredienser = ingredienser.values()

        ingredienser.sort(key=lambda x: x.vare, reverse=baklengsSortering)

        return ingredienser

class ingrediensGruppe(object):
    #Klasse for håndtering av mange ingredienser med samme enhet og samme vare.
    def __init__(self,ing):
        self.enhet = ing.enhet
        self.vare = ing.vare

        self.ingredienser = []
        self.leggTil(ing)

    def mengde(self):
        #Returnerer summen av mengden til enheten:
        mengde = 0
        for ing in self.ingredienser:
            if ing.mengde():
                mengde += ing.mengde()
        if not mengde:
            mengde = None
        return mengde

    def mengdeTekst(self):
        return self.enhet.mengdeTekst(self.mengde())

    def leggTil(self,ing):
        #Legg til ingrediens til gruppen
        if self.sammenlignbar(ing):
            if isinstance(ing,ingrediensGruppe):
                ing = ing.ingredienser
            elif isinstance(ing,ingrediens):
                ing = [ing]
            self.ingredienser += ing
        else:
            raise Exception('Ingrediens eller enhet er ikke sammenlignbare.')

    def sammenlignbar(self,ing):
        #Sjekker om to oppskrifter er sammenlignbare og kan summeres.
        if self.vare == ing.vare and self.enhet.grunnenhet == ing.enhet.grunnenhet:
            return True
        else:
            return False

    def kommentarTekst(self):
        #Print ut en kommaseparert liste av kommentarer til matvarene.
        return ', '.join([ing.kommentar for ing in self.ingredienser if ing.kommentar])


    def komponentTekst(self):
        komponenter = []
        for ing in self.ingredienser:
            if ing.oppskrift:
                oppskNavn = ing.oppskrift.navn
            else:
                oppskNavn = 'annet'

            if ing.mengde():
                    if ing.oppskrift:
                        komponenter += ['%s til %s' % (self.enhet.mengdeTekst(ing.mengde()),oppskNavn)]
                    else:
                        komponenter += ['%s til %s' % (self.enhet.mengdeTekst(ing.mengde()),oppskNavn)]
            else:
                komponenter += [oppskNavn]


        if len(komponenter) == 1:
            komponentTekst = oppskNavn
        else:
            komponentTekst = ', '.join(komponenter)

        return komponentTekst

class ingrediens(object):
    #Klasse for å håndtere en enkelt ingrediens, med enhet, mengde, skalering og
    #behandling.
    def __init__(self,ingTekst,oppsk=[]):

        self.antall,antallTekst = self.tolkAntall(ingTekst)
        ingTekst = re.sub(antallTekst,'',ingTekst,1).strip()

        self.enhet,enhTekst = self.tolkEnhet(ingTekst)
        ingTekst = re.subn(enhTekst,'',ingTekst,1)[0].strip()

        self.kommentar,kommentarTekst = self.tolkKommentar(ingTekst)
        for k in kommentarTekst:
            ingTekst = re.sub(k,'',ingTekst).strip()

        vare = ingTekst

        self.vare = vare
        self.oppskrift = oppsk

    def mengde(self):
        #Returnerer summen av mengden til enheten:
        mengde = None
        if self.antall and self.oppskrift:
                mengde = self.antall*self.enhet.mengdeJustering*self.oppskrift.personer/self.oppskrift.oppskriftPersoner
        elif self.antall and not self.oppskrift:
            mengde = self.antall*self.enhet.mengdeJustering
        else:
            mengde = None #None betyr at vi trenger varen, men mengde er uviktig. Eks: Pepper, olivenolje, friske urter, etc.

        return mengde

    def mengdeTekst(self):
        return self.enhet.mengdeTekst(self.mengde())

    def tolkAntall(self,ing):
        #Tolke hva som er det angitte antallet av en ingrediens.

        tallForm = '(?:(?P<teller>\d+)/(?P<nevner>\d+)|(?P<tall>\d+(?:[\.,]\d+)?))'

        tallKombo = u'^(?:ca|omtrent|minst)? ?%s(?:[ -]+%s)?' % (tallForm,tallForm)

        tall = tregex.find(tallKombo,ing)

        if tall:
            alleTall = []
            antallTekst = tall[0]
            tall = tregex.name(tallForm,antallTekst)
            for t in tall:
                if t['tall']:
                    alleTall += [float(t['tall'].replace(',','.'))]
                elif t['teller'] and t['nevner']:
                    alleTall += [float(t['teller'])/float(t['nevner'])]
                else:
                    raise Exception(u'Dårlig tallformatering i ingrediens %s' % ing)
            antall = max(alleTall)
        else:
            antall = None
            antallTekst = ''

        return [antall,antallTekst]

    def tolkEnhet(self,ing):
        #Tolke mengdeenheten til en gitt ingrediens.
        for k,v in enhetsListe.items():
            enh = v.treff(ing)
            if enh:
                enhTekst = v.treffTekst(ing)
                break
        return enh,enhTekst

    def tolkKommentar(self,ing):
        kommentarTekst = re.findall('\(.*?\)|, .*?$',ing)
        if kommentarTekst:
            tekst = [re.findall(u'\((.*?)\)|, (.*?)$',v,re.UNICODE)[0] for v in kommentarTekst]
            kommentar = []
            for t in tekst:
                kommentar += [v for v in t if v]
            kommentar = ', '.join(kommentar)
            kommentarTekst = [re.escape(k) for k in kommentarTekst]
        else:
            kommentar = ''
            kommentarTekst = ''
        return kommentar, kommentarTekst


class kokebok(object):
    #Klasse for generering av kokebokobjekter fra en kokebok-yaml-fil.

    def __init__(self,kokebokFil):
        #Laste kokebok.yaml og studere innholdet.

        self.oppskrifter = {}

        with open(kokebokFil,'r') as fil:
            kokebok = yaml.load(fil)

        for k,v in kokebok['oppskrifter'].items():
            v['navn'] = k
            self.oppskrifter[k] = oppskrift(v)

    def finnOppskrift(self,soketekst = '',brukteOppskrifter = []):
        #Metode løper gjennom kokeboka og finner en oppskrift som oppfyller
        #kriteriene av navn og inneholder. Navn kan være omtrentlig treff,
        #og inneholder kan være en ingrediens eller en kategori (eks: fisk).
        #
        #Metoden returnerer en kopi av objektet, og ikke en lenke til det
        #faktiske objektet i kokeboka.

        fuzzyNameMatchLimit = 0.8

        retur = None

        soketekst = soketekst.lower()

        oppskrifter = {k:v for k,v in self.oppskrifter.items() if not v in brukteOppskrifter}

        #Blank input:
        if not soketekst:
            retur = random.choice(oppskrifter.values())

        #Direct match:
        if soketekst in oppskrifter and not retur:
            retur = oppskrifter[soketekst]

        #Fuzzy name match
        if not retur:
            for o in self.oppskrifter:
                ratio = tregex.similarity(soketekst,o.lower())
                if ratio >= fuzzyNameMatchLimit:
                    retur = oppskrifter[o]

        #Hvis soketekst inneholder bare ett ord, anta at det er en kategori:
        if tregex.find(u'^\w+$',soketekst) and not retur:
            kategoriOppskrifter = []
            for o in oppskrifter.values():
                if soketekst in o.kategorier:
                    kategoriOppskrifter += [o]
            if kategoriOppskrifter:
                retur = random.choice(kategoriOppskrifter)

        #Til slutt, anta at det er en ingrediens:
        if not retur:
            ingrediensOppskrifter = []
            for o in oppskrifter.values():
                if soketekst in [i.vare for i in o.ingredienser.ingredienser()]:
                    ingrediensOppskrifter += [o]
                if ingrediensOppskrifter:
                    retur = random.choice(ingrediensOppskrifter)

        return copy.deepcopy(retur)


    def listAlleIngredienser(self):
        alleIngredienser = ingrediensListe()
        for v in self.oppskrifter.values():
            alleIngredienser.leggTil(v.ingredienser.ingredienser())

        for ing in alleIngredienser.ingredienser():
            print '%+20s\t%-30s\t%-30s' % (ing.mengdeTekst(),ing.vare,ing.komponentTekst())

class kokk(object):
    def __init__(self,kokeboksti):
        self.kokeboksti = kokeboksti
        self.handleliste = ingrediensListe()
        self.kokebok = kokebok(kokeboksti)
        self.oppskrifter = []
        self.ukeplanSti = ''

    def lesKokebok(self):
        self.kokebok = kokebok(self.kokeboksti)

    def lesUkeplan(self,ukeplanSti=''):
        #Parser en ukeplan:

        if not ukeplanSti:
            ukeplanSti = self.ukeplanSti
        else:
            self.ukeplanSti = ukeplanSti

        self.handleliste = ingrediensListe()
        self.ukeplan = []

        with open(ukeplanSti,'r') as fid:
            tekst = fid.readlines()

        for t in tekst[1:]:
            svar = self.tolkUkeplanRad(t)
            if isinstance(svar,ingrediens):
                self.handleliste.leggTil(svar)
            if isinstance(svar,dict):
                self.ukeplan += [svar]

        self.oppfriskUkemeny()

    def leggOppskrifterTilHandleliste(self):
        #Tar de gjeldende oppskriftene og legger ingrediensene til i handlelista.
        for r in self.oppskrifter:
            if r['oppskrift']:
                self.handleliste.leggTil(r['oppskrift'].ingredienser.ingredienser())

    def tolkUkeplanRad(self,rad):
        #Tolker en rad i ukeplanen.
        middagsdagForm = u'^(?P<dag>.*?):(?P<tekst>.*)$'
        matrettForm = u'^(?P<matrettTekst>.*?)(?:(?:til (?P<antallPersoner>\d+)(?: personer)?)|(?: [xX\*] ?(?P<antallPersonerGanger>\d+)))?$'
        kommentarForm = u'^(?:\xef\xbb\xbf)?#.*?'

        rad = rad.decode('utf-8')
        #Clean text:
        rad = tregex.re.sub(u'\\n',u'',rad)

        #Middagsdag:

        if tregex.find(kommentarForm,rad):
            #Kommentar, hopp over.
            return None
        elif tregex.find(middagsdagForm,rad):
            treff = tregex.smart(middagsdagForm,rad)[0]
            rett  = {}
            rett['finnOppskrift'] = True
            rett['oppskrift'] = None
            rett = dict(rett.items() +treff.items())

            if tregex.find('^-$',treff['tekst'].strip()):
                #Markert med bindestrek, altså ikke middagsdag:
                rett['finnOppskrift'] = False
                return rett
            else:
                treff = tregex.smart(matrettForm,treff['tekst'].strip())[0]
                rett = dict(rett.items() +treff.items())
                if rett['antallPersoner']:
                    rett['antallPersoner'] = int(rett['antallPersoner'])
                if rett['antallPersonerGanger']:
                    rett['antallPersonerGanger'] = int(rett['antallPersonerGanger'])
                return rett
        elif rad:
            #Ingrediens:
            return ingrediens(rad)

    def oppfriskUkemeny(self):
        #Ta ukeplanen og oppdatér oppskriftvalgene.
        self.oppskrifter = []
        for rett in self.ukeplan:
            if not rett['finnOppskrift']:
                #Oppskriftsfri dag, bare å la passere.
                pass
            else:
                oppsk = copy.deepcopy(self.kokebok.finnOppskrift(rett['matrettTekst'],[r['oppskrift'] for r in self.oppskrifter]))
                if rett['antallPersoner']:
                    oppsk.personer = rett['antallPersoner']
                elif rett['antallPersonerGanger']:
                    oppsk.personer = oppsk.oppskriftPersoner*rett['antallPersonerGanger']

                rett['oppskrift'] = oppsk
            self.oppskrifter += [rett]

    def printUkesmeny(self):
        #PROOF OF CONCEPT.
        #Den endelige klassen må være mer generell, og kun returnere en liste
        #eller et dictionary med den informasjonen som trengs.
        self.oppskrifter

        for o in self.oppskrifter:
            dag = o['dag']
            oppsk = o['oppskrift']
            if not oppsk and not o['finnOppskrift']:
                print '\n== %s: Ingen middag ==' % (dag)
            elif not oppsk and o['finnOppskrift']:
                print '\n== %s: NB: Ikke funnet noen oppskrift ved navn/kategori "%s" ==' % (dag,o['tekst'])
            else:
                self.handleliste.leggTil(oppsk.ingredienser.ingredienser()) #Legg til ingredienser i hovelista.

                print '\n== %s: %s til %s personer ==' % (dag,oppsk.navn,oppsk.personer)
                print oppsk.oppskrift

                for ing in oppsk.ingredienser.ingredienser():
                    if ing.kommentarTekst():
                        kommentar = ', ' + ing.kommentarTekst()
                    else:
                        kommentar = ''
                    print '%+15s\t%s%s' % (ing.mengdeTekst(),ing.vare,kommentar)

    def printOppskriftForslag(self):
        for rett in self.oppskrifter:
            if not rett['oppskrift'] and not rett['finnOppskrift']:
                print '%s: Ingen middag' % (rett['dag'])
            elif not rett['oppskrift'] and rett['finnOppskrift']:
                print '%s: NB: Ikke funnet noen oppskrift ved navn/kategori "%s"' % (rett['dag'],rett['tekst'])
            else:
                print '%s: %s' % (rett['dag'],rett['oppskrift'].navn)

    def printHandleliste(self):
        print '\n\nHANDLELISTE:'
        for ing in self.handleliste.ingredienser():
            print '%+15s\t%-30s' % (ing.mengdeTekst(),ing.vare)

    def sendTilWunderlist(self):
        wunderTob.sendToWunderlist('Handleliste',self.handleliste.ingredienserTekst(),self.handleliste.komponentTekst())

if __name__ == '__main__':
    path =  os.path.dirname(__file__)

    kokeboksti = os.path.join(path,'kokebok.yaml')

    kokken = kokk(kokeboksti)

    #kokk.kokebok.listAlleIngredienser()

    #kokk.lageUkesmeny()
    ukeplanSti = os.path.join(path,'ukeplan.txt')
    kokken.lesUkeplan(ukeplanSti)
    kokken.printOppskriftForslag()
    kokken.leggOppskrifterTilHandleliste()
    kokken.sendTilWunderlist()
