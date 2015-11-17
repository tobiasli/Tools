# Tools
[![Stories in Ready](https://badge.waffle.io/tobiasli/Tools.svg?label=ready&title=backlog)](http://waffle.io/tobiasli/Tools)<br/>
[![Build Status](https://travis-ci.org/tobiasli/Tools.svg?branch=master)](https://travis-ci.org/tobiasli/Tools)<br/>
[![Coverage Status](https://coveralls.io/repos/tobiasli/Tools/badge.svg?branch=master&service=github)](https://coveralls.io/github/tobiasli/Tools?branch=master)

Suite of tools for making my Python-day easier.

### tregex
Wrapper around the re-module, making my primary use of regex a lot smoother. Primary functions:

<b>smart</b>: Takes a pattern and a string, and returns:
- a list of dictionaries if match and named groups are present in pattern.
- a list of tuples if match and groups are present in pattern.
- a string if match and no capture groups are present in pattern.

If the user has a pattern with named groups, but only wants a simple match, <b>find</b> will only return the matched string. If the user has a pattern with named groups, but only wants group match, <b>group</b> will only return the grouped tuples.

<b>similarity</b>: Takes two strings and returns a score based on how similar the two strings are. Uses difflib.

### simpletimer
Two simple timer classes that can print the time to see how fast any process is running.

<b>SimpleTimer</b>: Very simple timer that starts a clock at construction, and can print time since construction.

<b>ProgressTimer</b>: Starts time at initiation along with the number of steps being calculated. Prints the progress in %, along with ETA.

### logFile
Simple logging class, with printing to file or send emails with attatchments.
