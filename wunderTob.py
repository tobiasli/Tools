# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
-------------------------------------------------------------------------------
 Name:          wunderTob
 Purpose:       Automated navigation of wunderlist. The Wunderlist API demanded
                a webserver, which i am not bothered to set up quite yet.

 Author:        Tobias Litherland

 Created:       16.04.2015
 Copyright:     (c) Tobias Litherland 2015


Logg:
    16.04.2015  First version of module. Try to get the hang of communicating
                with the rest API. This failed. API demands a webserver for
                communication. Will attempt to automate the process with
                selenium.
-------------------------------------------------------------------------------
'''
import datetime
import copy
import time
import re
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#Spesifikk liste:
url = r'https://www.wunderlist.com/webapp'
login = {'username':'tobiaslland@gmail.com','password':'dvegeg86'}
timeout = 50 #deciseconds

def sendToWunderlist(destinationList,tasks,loginInfo = login):
    print 1
    browserType = 'Firefox'
    browser = eval('webdriver.%s()' % browserType)
    browser.get(url)
    wait = WebDriverWait(browser, 10)
    print 2

    count = 0
    while count < timeout:
        print('.'),
        if 'login' in browser.current_url:
            wait.until(EC.element_to_be_clickable((By.NAME,'email'))).send_keys(loginInfo['username'])
            wait.until(EC.element_to_be_clickable((By.NAME,'password'))).send_keys(loginInfo['password'])
            parts = browser.find_elements_by_tag_name('input')
            for p in parts:
                if p.get_attribute('Value') == u'Logg på':
                    p.click()
            break
        else:
            time.sleep(0.1)
            count += 1

    print 3

    #Find correct list:
    ##try:
    ##    wait.until(EC.element_to_be_clickable((By.LINK_TEXT ,'Handleliste')))
    ##except:
    ##    raise Exception('List not found!')
    count = 0
    while count < timeout:
        print('.'),
        try:
            parts = browser.find_elements_by_class_name('title')
        except:
            pass
        if parts:
            for p in parts:
                try:
                    if p.text == destinationList:
                            p.click()
                            break
                except:
                    pass

        time.sleep(0.1)
        count += 1

    print 4

    #Add items to list:
    count = 0
    while count < timeout:
        print('.'),
        try:
            parts = browser.find_elements_by_tag_name('input')
        except:
            pass
        if parts:
            for p in parts:
                try:
                    if 'addTask' in p.get_attribute('class'):
                        p.send_keys(Keys.RETURN)
                        break
                except:
                    pass
        time.sleep(0.1)
        count += 1

    for p in parts:
        if 'addTask' in p.get_attribute('class'):
            for t in tasks:
                pass
                p.send_keys(t)
                p.send_keys(Keys.RETURN)

    print 5



if __name__ == "__main__":
    pass