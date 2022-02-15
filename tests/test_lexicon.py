"""
Define a suite a tests for the Lexicon module.
"""
from striplog import Lexicon


def test_lexicon():
    """All the tests...
    """
    lexicon = Lexicon.default()
    s = lexicon.__str__()
    assert s is not ''
    assert lexicon.__repr__() is not ''
    assert lexicon.find_synonym('Halite') == 'salt'
    assert len(lexicon.categories) == 5

    s = "lt gn ss w/ sp gy sh"
    answer = 'lighter green sandstone with spotty gray shale'
    assert lexicon.expand_abbreviations(s) == answer

    fname = "tests/data/lexicon.json"
    l = Lexicon.from_json_file(fname)
    assert l.__repr__() is not ''
