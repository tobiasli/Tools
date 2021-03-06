﻿# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
Name:        logger
Purpose:     Class for the handling of errors and messages. Contains methods
             for printing messages to file, screen, and send via email.
             Important to have the print to file/screen/email command within
             a try/finally clause to make sure that errors are returned before
             the program shuts down.
Author:      tobiasl
Created:     26.03.2014
Copyright:   (c) tobiasl 2014
--- History:
2014.03.27 TL    First stable version. Further updates should include classes
                 to export messages to various formats. First off is .txt.
2014.04.28 TL    Rewrote Message class to now also have methods for returning
                 a compiled string of all text in message object. Makes the
                 rest of the code a lot cleaner.
2014.04.29 TL    Added email method, to pass log as email content with
                 argument for attachments.
2014.05.05 TL    Added further documentation.
2014.10.23 TL    Added error tag to printFile. If ther are errors, and errorTag
                 equals True, then the file name is appended with '_error' (before
                 numbering indexes).

-------------------------------------------------------------------------------
'''

import datetime as time
import os
import smtplib
##from email.MIMEMultipart import MIMEMultipart
##from email.MIMEBase import MIMEBase
##from email.MIMEText import MIMEText
##from email import Encoders
##from email.Utils import formatdate

class Message(object):
    # Message object that contains all information regarding messages for a
    # single point in time. Can contain any number of individual messages for the
    # same time stamp. Contains both messages and errors in the same list,
    # separated by the error = True/False value.

    def __init__(self, text, timestamp=True, newline=True, error=False, warning=False):
        self.time = time.datetime.now()
        self.text = text
        self.timestamp = timestamp
        self.newline = newline
        self.error = error
        self.warning = warning

    def getMessage(self, newline=None):
        #Returns all text in message object as one ready formatted string.
        #The newline argument can override the newline of the message object.
        message = ''
        if isinstance(self.text,list):
           for text in self.text:
               message += self._compile_(text, newline)
        else:
             message += self._compile_(self.text, newline)
        return message

    def _compile_(self, text, newline=None):
        #Creates a ready formatted print string.
        #text = unicode(text, "UTF-8")
        stamp = ''
        if self.timestamp: stamp = '%s-' % self.time.strftime('%Y.%m.%d %H:%M:%S')

        line = ''

        if isinstance(newline,type(None)):
            newline = self.newline
        if newline: line = '\n'

        assert not (self.error and self.warning)
        label = ''
        if self.error: label = 'Error: '
        if self.warning: label = 'Warning: '

        return '%s%s%s%s' % (line, stamp, label, text)


class Log(object):
    #Creates a logfile instance that handles messages and can store them in a
    #text file.

    def __init__(self,dynamicPrintToScreen = False, timestamp = True):
        #File is the base name of the log file. The name will have a timestamp
        #appended, and the name will be incremented if there are several log
        #files with the same timestamp.
        #
        # dynamicPrintToScreen      boolean, if True, all message methods will
        #                                    print to screen as well as print
        #                                    to log.

        self.m = []  #List of Message objects.
        self.init = time.datetime.now()
        self.dynamicPrintToScreen = dynamicPrintToScreen
        self.timestamp = timestamp
        self.errorCount = 0
        self.warningCount = 0

    def addMessage(self, text, timestamp=None, newLine=True,toScreen = False):
        #Add message to log.
        #
        # Input:
        #       text            string/list, Message for log. Can be a string
        #                                    or a list of strings.
        #       timestamp       boolean, Add time stamp to message.
        #       newLine         boolean, Write message to new line in file
        #                                (True), or append to current (False).
        if timestamp is None: timestamp = self.timestamp
        self.m.extend([Message(text, timestamp, newLine)])
        if toScreen or self.dynamicPrintToScreen:
           print(self.m[-1].getMessage(newline=False))

    def addWarning(self, text, timestamp=None, newLine=True, toScreen=False):
        # Add warning message to log. Only difference to addMessage is the
        # warning = True, but the method is included for readability between
        # errors, warnings and messages.
        #
        # Input:
        #       text            string, Error message for log. Can be a string
        #                               or a list of strings.
        #       timestamp       boolean, Add time stamp to message.
        #       newLine         boolean, Write message to new line in file
        #                                (True), or append to current (False).
        if timestamp is None: timestamp = self.timestamp
        self.m.extend([Message(text, timestamp, newLine, warning=True)])
        self.warningCount += 1
        if toScreen or self.dynamicPrintToScreen:
           print(self.m[-1].getMessage(newline=False))

    def addError(self, text, timestamp=None, newLine=True, toScreen=False):
        # Add error message to log. Only difference to addMessage is the
        # error = True, but the method is included for readability between
        # errors and messages.
        #
        # Input:
        #       text            string, Error message for log. Can be a string
        #                               or a list of strings.
        #       timestamp       boolean, Add time stamp to message.
        #       newLine         boolean, Write message to new line in file
        #                                (True), or append to current (False).
        if timestamp is None: timestamp = self.timestamp
        self.m.extend([Message(text, timestamp, newLine, error=True)])
        self.errorCount += 1
        if toScreen or self.dynamicPrintToScreen:
           print(self.m[-1].getMessage(newline=False))

    def returnLogAsString(self, title='Run log'):
        # Return entire log as text:
        #
        # Input:
        #       title           string, The title of the log.
        return self._compileLogText_(title)

    def printLogToScreen(self, title='Run log'):
        # Print complete log to screen.
        #
        # Input:
        #       title           string, The title of the log.

        print(self._compileLogText_(title))

    def printLogToFile(self, path, namebase, title='Log', completeName=False, errorTag=False):
        # Create file. "name" is only the name base. Time stamp and file type are
        # added by the script. If completeName = True, then the filename in
        # "name" is taken as is, without adding timestamp or checking for
        # existing files.
        #
        # Input:
        #       path            string, Path to log folder.
        #       namebase        string, Log file name prefix. Datestamp
        #                               is added to this.
        #       title           string, The title of the log.
        #       completeName    boolean, If completeName = True, increments and
        #                                time stamps are not added to the name.
        #                                Assumes namebase also contains file
        #                                type suffix.

        if not completeName:
            namebase = self._addTimeStampToFileName_(namebase)

        if errorTag and self.errorCount > 0:
            nameSplit = namebase.split('.')
            nameSplit[-2] = nameSplit[-2] + '_error'
            namebase = '.'.join(nameSplit)

        if not completeName:
           namebase = self._getFileNameIncrement_(path, namebase)

        self.log_file_path = os.path.join(path, namebase)
        self.log_file = open(self.log_file_path, 'w')

        try:
            self.log_file.write(self._compileLogText_(title))
        finally:
            self.log_file.close()

    def _addTimeStampToFileName_(self,name):
        #Add initialization time stamp to file name:
        timename = self.init.strftime('%Y.%m.%d')
        filename = '%s_%s.txt' % (name, timename)
        return filename

    def _getFileNameIncrement_(self, path, filename):
        #Takes suggested file name and checks if file allready exist. If so,
        #add numeric increment to file name until unique name is found.

        name = '.'.join(filename.split('.')[0:-1])
        extension = filename.split('.')[-1]

        #Check if file allready exists in folder:
        files = os.listdir(path)
        dupCount = 1
        #Check for duplicates of both txt and xml files, incase there is need
        #for a copy of the xml as well.
        while filename in files:
            dupCount += 1
            filename = '%s (%d).%s' % (name, dupCount,extension)

        return filename

    def _compileLogText_(self,title):
        #Compile log text. Create a single string from the entire batch of
        #messages and errors added to the message handler object.
        logText = ''
        stringLen = len(title)
        logText += '%s\n' % ('-' * (stringLen + 8))
        logText += '--- %s %s\n' % (title, '---')
        logText += '%s\n' % ('-' * (stringLen + 8))
        logText += '%s = %s' % ('Run start time', self.init.strftime('%Y.%m.%d %H:%M:%S'))

        #Add all logged messages:
        for message in self.m:
            logText += message.getMessage()

        #Complete file, aka add summery text:
        logText += '\n\nRun complete.'
        logText += '\nNumber of warning messages logged: %d' % self.warningCount
        logText += '\nNumber of error messages logged: %d' % self.errorCount
        logText += '\nEnd of file.'

        try:
            logText = logText.decode('utf-8')
        except:
            pass

        return logText