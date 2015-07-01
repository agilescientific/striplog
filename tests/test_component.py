# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Component module.
"""

from striplog import Component
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

def test_init():
    rock = Component(r)
    assert rock.colour == 'grey'

def test_identity():
    rock = Component(r)
    rock2 = Component(r2)
    assert rock == rock2

    rock3 = Component(r3)
    assert rock != rock3

def test_summary():
    rock = Component(r)
    s = rock.summary(fmt="My rock: {lithology} ({colour}, {GRAINSIZE})")
    assert s == 'My rock: sand (grey, VF-F)'

def test_from_text():
    rock3 = Component(r3)
    lexicon = Lexicon.default()
    rock4 = Component.from_text('Grey coarse sandstone.', lexicon)
    assert rock3 == rock4
