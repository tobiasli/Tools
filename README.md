# Tools
Suite of tools for making my Python-day easier.

### arctools

Wrapper for making my gis-day easier. Two primary functions:

<b>tableToDict</b>: Take any database table and convert to a list of dictionaries (or a dictionary of dictionaries!). Supports grouping based on field attributes, and reading of only specific fields.

<b>dictToTable</b>: Take any list of dictionaries (or dictionary of dictionaries!) and convert to a database table. Supports insert, update and delete (the two latter based on key fields and keys to match correct entries).

### tregex
Wrapper around the re-module, making my primary use of regex a lot smoother. Primary functions:

<b>smart</b>: Takes a pattern and a string, and returns:
- a list of dictionaries if match and named groups are present in pattern.
- a list of tuples if match and groups are present in pattern.
- a string if match and no capture groups are present in pattern.
If the user has a pattern with named groups, but only wants a simple match, <b>find</b> will only return the matched string. If the user has a pattern with named groups, but only wants group match, <b>group</b> will only return the grouped tuples.

<b>similarity</b>: Takes two strings and returns a score based on how similar the two strings are. Uses difflib.

### dateParse
Class for parsing dates from arbitrary strings.

<b>parse</b>: Extremely flexible method for creating datetime objects from string formated dates. Very strong date detection, but at the cost of slow speed. Could do with some optimization.
