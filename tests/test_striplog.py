# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Striplog module.
"""

import numpy as np
import pytest

from striplog import Component
from striplog import Interval
from striplog import Legend
from striplog import Lexicon
from striplog import Striplog
from striplog.striplog import StriplogError

las3 = """~Lithology_Parameter
LITH .   Striplog         : Lithology source          {S}
LITHD.   MD               : Lithology depth reference {S}

~Lithology_Definition
LITHT.M                   : Lithology top depth       {F}
LITHB.M                   : Lithology base depth      {F}
LITHD.                    : Lithology description     {S}

~Lithology_Data | Lithology_Definition
  280.000,  299.986,  "Red, siltstone"
  299.986,  304.008,  "Grey, sandstone, vf-f"
  304.008,  328.016,  "Red, siltstone"
  328.016,  328.990,  "Limestone"
  328.990,  330.007,  "Red, siltstone"
  330.007,  333.987,  "Limestone"
  333.987,  338.983,  "Red, siltstone"
  338.983,  340.931,  "Limestone"
  340.931,  345.927,  "Red, siltstone"
  345.927,  346.944,  "Limestone"
  346.944,  414.946,  "Red, siltstone"
  414.946,  416.936,  "Grey, mudstone"
  416.936,  422.440,  "Red, heterolithic"
  422.440,  423.414,  "Grey, mudstone"
 """

csv_string = """  200.000,  230.329,  Anhydrite
                  230.329,  233.269,  Grey vf-f sandstone
                  233.269,  234.700,  Anhydrite
                  234.700,  236.596,  Dolomite
                  236.596,  237.911,  Red siltstone
                  237.911,  238.723,  Anhydrite
                  238.723,  239.807,  Grey vf-f sandstone
                  239.807,  240.774,  Red siltstone
                  240.774,  241.122,  Dolomite
                  241.122,  241.702,  Grey siltstone
                  241.702,  243.095,  Dolomite
                  243.095,  246.654,  Grey vf-f sandstone
                  246.654,  247.234,  Dolomite
                  247.234,  255.435,  Grey vf-f sandstone
                  255.435,  258.723,  Grey siltstone
                  258.723,  259.729,  Dolomite
                  259.729,  260.967,  Grey siltstone
                  260.967,  261.354,  Dolomite
                  261.354,  267.041,  Grey siltstone
                  267.041,  267.350,  Dolomite
                  267.350,  274.004,  Grey siltstone
                  274.004,  274.313,  Dolomite
                  274.313,  294.816,  Grey siltstone
                  294.816,  295.397,  Dolomite
                  295.397,  296.286,  Limestone
                  296.286,  300.000,  Volcanic
                  """


def test_error():
    with pytest.raises(StriplogError):
        Striplog([])


def test_striplog():
    r1 = Component({'lithology': 'sand'})
    r2 = Component({'lithology': 'shale'})
    r3 = Component({'lithology': 'limestone'})

    # Bottom up: elevation order
    iv1 = Interval(120, 100, components=[r1])
    iv2 = Interval(150, 120, components=[r2])
    iv3 = Interval(180, 160, components=[r1, r2])
    iv4 = Interval(200, 180, components=[r3, r2])

    s1 = Striplog([iv1, iv2])
    s2 = Striplog([iv3, iv4])
    s = s1 + s2
    assert s.order == 'elevation'
    assert len(s) == 4
    assert s.start == 100
    assert s.stop == 200
    assert s.__repr__() is not ''
    assert s.__str__() is not ''

    # Top down: depth order
    iv1 = Interval(80, 120, components=[r1])
    iv2 = Interval(120, 150, components=[r2])
    iv3 = Interval(180, 200, components=[r1, r2])
    iv4 = Interval(200, 250, components=[r3, r2])

    s = Striplog([iv1, iv2, iv3, iv4])
    assert s.order == 'depth'
    assert len(s) == 4
    assert s.start == 80
    assert s.stop == 250

    l = [iv.thickness for iv in s]
    assert len(l) == 4

    s[2] = Interval(180, 190, components=[r1, r2])
    assert len(s.find_gaps()) == 2


def test_from_image():
    legend = Legend.builtin('NSDOE')
    imgfile = "tutorial/M-MG-70_14.3_135.9.png"
    striplog = Striplog.from_img(imgfile, 200, 300, legend=legend)
    assert len(striplog) == 26
    assert striplog[-1].primary.summary() == 'Volcanic'
    assert np.floor(striplog.find('sandstone').cum) == 15
    assert striplog.depth(260).primary.lithology == 'siltstone'
    assert striplog.to_las3() is not ''
    assert striplog.to_log()[5] == 2.0
    assert striplog.cum == 100.0
    assert striplog.thickest().primary.lithology == 'anhydrite'
    assert striplog.thickest(n=7)[1].primary.lithology == 'sandstone'
    assert striplog.thinnest().primary.lithology == 'dolomite'
    assert striplog.thinnest(n=7)[1].primary.lithology == 'siltstone'

    indices = [2, 7, 20]
    del striplog[indices]
    assert len(striplog.find_gaps()) == len(indices)

    striplog.prune(limit=1.0)
    assert len(striplog) == 14

    striplog.anneal()
    assert not striplog.find_gaps()  # Should be None

    rock = striplog.find('sandstone')[1].components[0]
    assert rock in striplog


def test_from_csv():
    lexicon = Lexicon.default()
    strip2 = Striplog.from_csv(csv_string, lexicon=lexicon)
    assert len(strip2.top) == 7


def test_from_las3():
    s = Striplog.from_las3(las3)
    assert len(s) == 14


def test_from_array():
    lexicon = Lexicon.default()

    a = [(100, 200, 'red sandstone'),
         (200, 250, 'grey shale'),
         (200, 250, 'red sandstone with shale stringers'),
         ]
    s = Striplog._from_array(a, lexicon=lexicon)
    assert s.__str__() != ''


def test_histogram():
    lexicon = Lexicon.default()
    striplog = Striplog.from_las3(las3, lexicon=lexicon)
    _, counts = striplog.histogram()
    assert counts == (123, 6, 6, 5, 3)
