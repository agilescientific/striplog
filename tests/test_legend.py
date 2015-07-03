# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Legend module.
"""
import pytest

from striplog import Legend
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

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}

r3 = {'colour': 'red',
      'grainsize': 'vf-f',
      'lithology': 'sandstone'}


def test_legend():

    legend = Legend.from_csv(csv_text)
    assert legend[0].colour == '#f7e9a6'
    assert legend.max_width == 5
    assert legend.__str__() != ''
    assert legend.__repr__() != ''

    rock = Component(r)
    assert legend.get_colour(rock) == '#eeeeee'

    rock3 = Component(r3)
    assert legend.get_colour(rock3) == '#ffdbba'
    assert legend.get_width(rock3) == 3.0

    c = legend.get_component('#f7e9a6')
    assert c.lithology == 'sandstone'

    colours = [d.colour for d in legend]
    assert len(colours) == 8

    l = Legend.random([rock, rock3])
    assert l != legend
    assert getattr(l[-1], 'colour') != ''
    assert l.to_csv() != ''

    summed = legend + l
    assert len(summed) == 10


def test_error():
    legend = Legend.from_csv(csv_text)
    rock = Component(r)
    with pytest.raises(LegendError):
        legend + rock
