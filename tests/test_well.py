# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Well module.
"""

from striplog import Well
from striplog import Striplog
from striplog import Legend

def test_well():

    fname = 'tutorial/P-129_out.LAS'
    well = Well(fname)
    assert well.well.DATE.data == '10-Oct-2007'
    assert well.data['GR'][0] == 46.69865036

    legend = Legend.default()
    f = 'tutorial/P-129_280_1935.png'
    name, start, stop = f.strip('.png').split('_')
    striplog = Striplog.from_img(f, float(start), float(stop), legend=legend, tolerance=35)
    well.add_striplog(striplog, "striplog")
    assert well.striplog.striplog.source == 'Image'
    assert well.striplog.striplog.start == 280.0
