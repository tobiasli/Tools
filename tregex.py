"""
-------------------------------------------------------------------------------
 Name:        tregex
 Purpose:     Wrapper that makes my everyday use of regex much smoother.

 Author:      Tobias Litherland

 Created:     10.04.2015
 Copyright:   (c) Tobias Litherland 2015

 GitHub:      https://github.com/tobiasli/Tools
-------------------------------------------------------------------------------
"""

import re
import difflib

DEFAULT_FLAG = re.UNICODE | re.DOTALL
NAMED_GROUP_DETECTION = '(\(\?P<\w+>)'
NAMED_GROUP_REFERANCE_DETECTION = '\(\?\(\w+\)'
DEFAULT_SEARCH_SCORE_CUTOFF = 0.6
CONTENT_MATCH_DEFAULT_SCORE = 0.01


class UnknownMethodError(Exception):
    pass


def _process(pattern, string, output='smart', flags=DEFAULT_FLAG):
    # Returns the named groups from a pattern match directly, insted of going
    # through the regular parsing.
    r = re.compile(pattern, flags)
    result = [found for found in r.finditer(string)]
    if result:
        return_list = []

        if output == 'smart':
            if result[0].groupdict():
                output = 'name'
            elif result[0].groups():
                output = 'group'
            else:
                output = ''

        if not output:
            for m in result:
                return_list += [m.group()]
        elif output == 'name':
            for m in result:
                return_list += [m.groupdict()]
        elif output == 'group':
            for m in result:
                return_list += [m.groups()]
        else:
            raise UnknownMethodError("Unknown method {} for argument 'output'.".format(output))

        return return_list
    else:
        return []


def name(pattern, string, flags=DEFAULT_FLAG):
    return _process(pattern, string, output='name', flags=flags)


def match(pattern, string, flags=DEFAULT_FLAG):
    # Only return strings matching pattern, not considering any grouping. Will
    # remove any named groups from pattern before compiling.
    pattern = re.sub(NAMED_GROUP_DETECTION, '(', pattern)  # Remove named groups.
    pattern = re.sub(NAMED_GROUP_REFERANCE_DETECTION, '(', pattern)  # Remove named groups.
    return _process(pattern, string, output='', flags=flags)


def group(pattern, string, flags=DEFAULT_FLAG):
    # Only return strings matching groups. Will remove any named groups from
    # pattern before compiling.

    pattern = re.sub(NAMED_GROUP_DETECTION, '(', pattern)  # Remove named groups.
    return _process(pattern, string, output='group', flags=flags)


def smart(pattern, string, flags=DEFAULT_FLAG):
    return _process(pattern, string, output='smart', flags=flags)


def similarity(string1, string2):
    # Returns a score based on the degree of match between to strings:
    return difflib.SequenceMatcher(None, string1, string2).ratio()


def find_best(search_string, search_list, score_cutoff=0, case_sensitive=False, return_scores=False):
    """Fuzzy name search from a list of strings.

    Args:
        search_string (str): The string used to find a sufficient match in the search_list.
        search_list (list): A list of strings where we search for one or more matches.
        score_cutoff (int): The score cutoff of the results
        case_sensitive (bool): Specify if search is case sensitive or not.
        return_scores (bool): Return tuples with matches and scores instead if just matches.


    Returns:
        Returns the best match from the search_list
    """
    result = find(search_string=search_string,
                  search_list=search_list,
                  score_cutoff=score_cutoff,
                  case_sensitive=case_sensitive,
                  scores=return_scores)
    if result:
        return result[0]
    else:
        return None


def find(search_string, search_list, score_cutoff=DEFAULT_SEARCH_SCORE_CUTOFF, case_sensitive=False, scores=False):
    """Fuzzy name search from a list of strings.

    Args:
        search_string (str): The string used to find a sufficient match in the search_list.
        search_list (list): A list of strings where we search for one or more matches.
        score_cutoff (float): The score cutoff of the results
        case_sensitive (bool): Specify if search is case sensitive or not.
        scores (bool): Return tuples with matches and scores instead if just matches.


    Returns:
        Returns a list of items that sufficiently match the search_string
    """

    if not case_sensitive:
        search_string_p = search_string.lower()
        search_list_p = [s.lower() for s in search_list]
    else:
        search_string_p = search_string
        search_list_p = search_list

    similarity_scores = [similarity(search_string_p, item) for item in search_list_p]
    scores_cutoff = [(score, item) for score, item in zip(similarity_scores, search_list) if score >= score_cutoff]
    scores_sorted = sorted(scores_cutoff, key=lambda x: x[0], reverse=True)

    # Get the items which have a content match even if the score is too low:
    # Keep the length of the strings, so that the shortest strings get the highest match:
    contains_match = [orig for orig, case in zip(search_list, search_list_p)
                      if search_string_p in case
                      and orig not in [item[1] for item in scores_sorted]]
    contains_sorted = sorted(contains_match, key=lambda x: len(x), reverse=False)

    result = scores_sorted + [(CONTENT_MATCH_DEFAULT_SCORE, item) for item in contains_sorted]

    if not result:
        return []

    if scores:
        return result
    else:
        return [item[1] for item in result]
