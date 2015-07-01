# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Legend module.
"""

from striplog import Legend
from striplog import Component

l = u"""colour, width, component lithology, component colour, component grainsize
#FFFFFF, 0, , , 
#F7E9A6, 3, Sandstone, Grey, VF-F
#FF99CC, 2, Anhydrite, , 
#DBD6BC, 3, Heterolithic, Grey, 
#FF4C4A, 2, Volcanic, , 
#86F0B6, 5, Conglomerate, , 
#FF96F6, 2, Halite, , 
#F2FF42, 4, Sandstone, Grey, F-M
#DBC9BC, 3, Heterolithic, Red, 
#A68374, 2, Siltstone, Grey, 
#A657FA, 3, Dolomite, , 
#FFD073, 4, Sandstone, Red, C-M
#A6D1FF, 3, Limestone, , 
#FFDBBA, 3, Sandstone, Red, VF-F
#FFE040, 4, Sandstone, Grey, C-M
#A1655A, 2, Siltstone, Red, 
#363434, 1, Coal, , 
#664A4A, 1, Mudstone, Red, 
#666666, 1, Mudstone, Grey, """

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}

r3 = {'colour': 'red',
      'grainsize': 'vf-f',
      'lithology': 'sandstone'}


def test_legend():

    legend = Legend.from_csv(l)
    assert legend[1].colour == '#f7e9a6'

    rock = Component(r)
    assert legend.get_colour(rock) == '#eeeeee'

    rock3 = Component(r3)
    assert legend.get_colour(rock3) == '#ffdbba'
    assert legend.get_width(rock3) == 3.0

    c = legend.get_component('#f7e9a6')
    assert c.lithology == 'sandstone'

    colours = [d.colour for d in legend]
    assert len(colours) == 19
