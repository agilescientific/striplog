# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Lexicon module.
"""

from striplog import Lexicon

def test_lexicon():
    lexicon = Lexicon.default()
    assert lexicon.find_synonym('Halite') == 'salt'

    s = "lt gn ss w/ sp gy sh"
    answer = 'lighter green sandstone with spotty gray shale'
    assert lexicon.expand_abbreviations(s) == answer
