"""
Define a suite a tests for the Component module.
"""
import pytest

from striplog.rock import Rock
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

r6 = {'grainsize': 'Coarse',
      'colour': 'Grey',
      'lithology': None}

r7 = {'coords': (123, 456)}

r8 = {'coords': (123, 456),
      'None value': None}

def test_init():
    """Test Rock() for backward compatibility.
    """
    with pytest.warns(DeprecationWarning):
        rock = Rock(r)
    assert rock

    rock = Component(r)
    assert rock.colour == 'grey'


def test_component_html():
    """
    For jupyter notebook.

    Hard to test this because attributes are returned in random order.
    """
    r = {'lithology': 'sand'}
    rock = Component(r)
    html = """<table><tr><td><strong>lithology</strong></td><td>sand</td></tr></table>"""
    assert rock._repr_html_() == html


def test_identity():
    """
    Test equals.
    """
    rock = Component(r)
    assert rock != 'non-Component'

    rock2 = Component(r2)
    assert rock == rock2

    rock3 = Component(r3)
    assert rock != rock3


def test_summary():
    """
    Test ability to generate summaries.
    """
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
    """
    Test generation from strings.
    """
    rock3 = Component(r3)
    lexicon = Lexicon.default()
    s = 'Grey coarse sandstone.'
    rock4 = Component.from_text(s, lexicon)
    assert rock3 == rock4
    rock5 = Component.from_text(s, lexicon, required='not there')
    assert not rock5  # Should be None

def test_None():
    """
    Test generation with None
    """
    rock8 = Component(r8)
    assert rock8 == Component({'coords': (123, 456)})

def test_tuple():
    """
    Test generation from tuples
    """
    rock7 = Component(r7)
    assert rock7 == Component({'coords': (123, 456)})
