"""
Define a suite a tests for the Legend module.
"""
import pytest

from striplog import Legend
from striplog import Decor
from striplog import Component
from striplog.legend import LegendError

csv_text = u"""colour, width, component lithology, component colour, component grainsize
#F7E9A6, 3, Sandstone, Grey, VF-F
#FF99CC, 2, Anhydrite, ,
#DBD6BC, 3, Heterolithic, Grey,
#FF4C4A, 2, Volcanic, ,
#86F0B6, 5, Conglomerate, ,
#FFD073, 4, Sandstone, Red, C-M
#A6D1FF, 3, Limestone, ,
#FFDBBA, 3, Sandstone, Red, VF-F"""

csv_duplicate = u"""colour, width, component lithology, component colour, component grainsize
#F7E9A6, 3, Sandstone, Grey, VF-F
#FF99CC, 2, Anhydrite, ,
#FF99DD, 3, Anhydrite, ,
#DBD6BC, 3, Heterolithic, Grey,"""

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}

r3 = {'colour': 'red',
      'grainsize': 'vf-f',
      'lithology': 'sandstone'}


def test_legend():
    """Test all the basics.
    """
    legend = Legend.from_csv(text=csv_text)
    assert legend[0].colour == '#f7e9a6'
    assert legend.max_width == 5
    assert legend.__str__() != ''
    assert legend.__repr__() != ''

    assert len(legend[[3, 4]]) == 2
    assert len(legend[3:5]) == 2

    rock = Component(r)
    assert legend.get_colour(rock) == '#eeeeee'
    assert rock not in legend

    d = Decor({'colour': 'red',
               'component': rock})
    length = len(legend)
    legend[3] = d
    assert len(legend) == length
    assert legend[3].component == rock
    assert d in legend

    rock3 = Component(r3)
    assert legend.get_colour(rock3) == '#ffdbba'
    assert legend.get_width(rock3) == 3.0

    c = legend.get_component('#f7e9a6')
    assert c.lithology == 'sandstone'
    c2 = legend.get_component('#f7e9a7', tolerance=30)
    assert c2.lithology == 'sandstone'

    colours = [d.colour for d in legend]
    assert len(colours) == 8

    assert Legend.random(rock3)[0].colour != ''

    l = Legend.random([rock, rock3])
    assert len(l) == 2
    assert getattr(l[-1], 'colour') != ''
    assert l.to_csv() != ''
    assert l.max_width == 1.0

    l = Legend.random([rock, rock3], width=True, colour='#abcdef')
    assert getattr(l[0], 'colour') == '#abcdef'

    # Test sums.
    summed = legend + l
    assert len(summed) == 10

    summed_again = legend + d
    assert len(summed_again) == 9

    summed_again_again = d + legend
    assert len(summed_again_again) == 9

    # Test equality.
    assert not d == legend


def test_legend_builtins():
    """Test the builtins.
    """
    assert len(Legend.builtin('nsdoe')) == 18
    assert len(Legend.builtin('nagmdm__6_2')) == 206

    # And builtin timescale.
    assert len(Legend.builtin_timescale('isc')) == 240


def test_tolerance_warning(recwarn):
    """Test warning triggers if tolerance too low.
    """
    legend = Legend.from_csv(text=csv_text)
    legend.get_component('#f7e9a7', tolerance=0)
    w = recwarn.pop()
    assert issubclass(w.category, UserWarning)
    assert 'tolerance of 0' in str(w.message)
    assert w.lineno


def test_duplicate_warning(recwarn):
    """Test warning triggers if duplicate component in CSV.
    """
    Legend.from_csv(text=csv_duplicate)
    w = recwarn.pop()
    assert issubclass(w.category, UserWarning)
    assert 'duplicate' in str(w.message)
    assert w.lineno


def test_error():
    """Test errors are raised.
    """
    rock = Component(r)

    # Adding incompatible things
    legend = Legend.from_csv(text=csv_text)
    with pytest.raises(LegendError):
        _ = legend + rock
        assert _

    # Tolerance not allowed.
    with pytest.raises(LegendError):
        legend.get_component('#f7e9a7', tolerance=-1)
