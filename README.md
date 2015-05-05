# Tools
Suite of tools for making my Python-day easier.

<b>arctools</b>

Wrapper for making my gis-day easier. Two primary functions:

<i>tableToDict</i>

Takes any given database table, feature class or shapefile as unput, and returns a list containing all rows, or a dictionary containin all rows with the contents of a specified keyFields as dictionary keys.

<i>dictToTable</i>

The opposite as tableToDict, with options to add, overwrite and update table contains according to a given key field.

<b>tregex</b>
Wrapper around the re-module, making the regular expressions slightly simpler to use. Primary function:

<i>smart</i> 
Takes a pattern and a string, and returns
- a list of dictionaries if named groups are present in pattern.
- a list of tuples if groups are present in pattern.
- a list of strings if no capture groups are present in pattern.
If the user has a pattern with named groups, but only wants a simple match, use find to only return string even if the pattern contains groups or named groups.

<i>similarity</i>
Takes two strings and returns a score based on how similar the two strings are. Can be used for fuzzy searching of strings.
