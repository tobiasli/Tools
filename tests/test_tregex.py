"""
Tests copied and structured from https://github.com/tobiasli/Tools
"""

import pytest

import tregex

FIND_TEST_CASES = [
    (r'nisse \w+ \d fjell', 'nisse fjes 3 fjell'),
    (r'(?P<bogus_named_capture>nisse) \w+ \d fjell', 'nisse fjes 3 fjell'),
    (r'(?i)(nisse) \w+ \d fjell', 'Nisse FJES 3 fjell'),
]
FIND_TEST_CASES_TYPES = [str, dict, tuple]

GROUP_TEST_CASES = [
    (r'(nisse) (\w+) (\d) (fjell)', 'nisse fjes 3 fjell', ('nisse', 'fjes', '3', 'fjell')),
]

NAMED_TEST_CASES = [
    (r'^(?P<account>[\w\.]+)@(?P<host>[\w\.]+)\.(?P<domain>\w+)$', 'tobias.litherland@statkraft.com', [{'account': 'tobias.litherland', 'host': 'statkraft', 'domain': 'com'}]),
    (r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})', '2018-02-01 22:21:41', [{'year': '2018', 'month': '02', 'day': '01', 'hour': '22', 'minute': '21', 'second': '41'}])
]

SEARCH_LIST = ['Stavern', 'Larvik', 'Sandefjord', 'Tønsberg', 'Åsgårdstrand', 'Horten', 'Holmestrand']
SEARCH_MAPPING = {'strand': ['Holmestrand', 'Åsgårdstrand', 'Stavern'], 'naberg': ['Tønsberg'], 'larv': ['Larvik']}


def test_tregex_process():
    try:
        tregex._process(r'\d+', 'rthrth234234rthrth', output='this is not an output')
        assert False, 'The above method call should have failed with an TregexUnknownMethodError.'
    except tregex.TregexUnknownMethodError:
        pass

    nothing_found = tregex._process('nisse', 'troll', output='smart')
    assert not nothing_found


def test_tregex_match():
    for pattern, candidate in FIND_TEST_CASES:
        assert tregex.match(pattern, candidate), candidate


@pytest.mark.parametrize('pattern, candidate, response', GROUP_TEST_CASES)
def test_tregex_group(pattern, candidate, response):
    assert tregex.to_tuple(pattern, candidate), response


def test_tregex_smart():
    for case, instance in zip(FIND_TEST_CASES, FIND_TEST_CASES_TYPES):
        assert isinstance(tregex.smart(case[0], case[1])[0], instance)

@pytest.mark.parametrize('pattern, string, match', NAMED_TEST_CASES)
def test_tregex_name(pattern, string, match):
    assert tregex.to_dict(pattern, string) == match


def test_tregex_find():
    for search, match in SEARCH_MAPPING.items():
        result = tregex.find(search, SEARCH_LIST)

        assert len(result) > 0
        assert result[0] in match


def test_tregex_find_scores():
    result = tregex.find_scores('larvik', SEARCH_LIST, score_cutoff=0)
    for score, match in result:
        # print(match, score)
        assert isinstance(match, str)
        assert isinstance(score, (float, int))


def test_tregex_find_best():
    result = tregex.find_best('larvik', SEARCH_LIST, score_cutoff=1)
    assert result in SEARCH_LIST

    result = tregex.find_best('larvik', SEARCH_LIST, score_cutoff=1, case_sensitive=True)
    assert not result
