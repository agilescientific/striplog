# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Decor module.
"""

from striplog import Decor
from striplog import Component

def test_decor():

    r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}
    rock = Component(r)

    d = {'color': '#86F0B6',
         'component': rock,
         'width': 3}
    decor = Decor(d)

    assert decor.component.colour == 'grey'
    assert decor.colour == '#86f0b6'
    assert decor.rgb == (134, 240, 182)
