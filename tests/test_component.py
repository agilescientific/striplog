# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Component module.
"""
import pytest

from striplog.rock import Rock
from striplog import Component
from striplog.component import ComponentError
from striplog import Lexicon

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}

r2 = {'grainsize': 'VF-F',
      'colour': 'Grey',
      'lithology': 'Sand'}

r3 = {'grainsize': 'Coarse',
      'colour': 'Grey',
      'lithology': 'Sandstone'}

r6 = {'grainsize': 'Coarse',
      'colour': 'Grey',
      'lithology': None}


def test_rock():
    rock = Rock(r)
    assert rock


def test_init():
    rock = Component(r)
    assert rock.colour == 'grey'


def test_identity():
    rock = Component(r)
    assert rock != 'non-Component'

    rock2 = Component(r2)
    assert rock == rock2

    rock3 = Component(r3)
    assert rock != rock3


def test_summary():
    rock = Component(r)
    s = rock.summary(fmt="My rock: {lithology} ({colour}, {grainsize!u})")
    assert s == 'My rock: sand (grey, VF-F)'

    rock6 = Component(r6)
    s = rock6.summary(fmt="My rock: {lithology}")
    assert s == 'My rock: _'

    empty = Component({})
    d = "String"
    assert not empty  # Should have False value
    assert empty.summary(default=d) == d


def test_from_text():
    rock3 = Component(r3)
    lexicon = Lexicon.default()
    s = 'Grey coarse sandstone.'
    rock4 = Component.from_text(s, lexicon)
    assert rock3 == rock4
    rock5 = Component.from_text(s, lexicon, required='not there')
    assert not rock5  # Should be None
