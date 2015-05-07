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

def sendToWunderlist(destinationList,tasks,descriptions,loginInfo = login):
    browserType = 'Firefox'
    browser = eval('webdriver.%s()' % browserType)
    browser.get(url)
    wait = WebDriverWait(browser, 10)

    count = 0
    while count < 50:
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

    #Find correct list:
    ##try:
    ##    wait.until(EC.element_to_be_clickable((By.LINK_TEXT ,'Handleliste')))
    ##except:
    ##    raise Exception('List not found!')
    count = 0
    while count < 50:
        try:
            parts = browser.find_elements_by_class_name('title')
            break
        except:
            time.sleep(0.1)
            count += 1
    if parts:
        for part in parts:
            if destinationList == part.text:
                part.click()

    #Add items to list:
    count = 0
    while count < 50:
        try:
            parts = browser.find_elements_by_tag_name('input')
            break
        except:
            time.sleep(0.1)
            count += 1

    for p in parts:
        if 'addTask' in p.get_attribute('class'):
            for t,d in zip(tasks,descriptions):
                browser.find_elements_by_tag_name('taskItem')
                p.send_keys(t)
                p.send_keys(Keys.RETURN)

                wait.until(EC.element_to_be_clickable((By.TAG,'taskItem')))
                taskItems = browser.find_elements_by_tag_name('taskItem')
                taskItems[0].double_click()
                wait.until(EC.element_to_be_clickable((By.TAG,'note-body selectable'))).send_keys(d)
                wait.until(EC.element_to_be_clickable((By.TAG,'note-body selectable'))).send_keys(Keys.RETURN)




if __name__ == "__main__":
    pass