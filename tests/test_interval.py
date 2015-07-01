# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Interval module.
"""

from striplog import Lexicon
from striplog import Interval

def test_interval():

    lexicon = Lexicon.default()
    interval = Interval(20, 40, "Grey sandstone.", lexicon=lexicon)
    assert interval.primary.lithology == 'sandstone'
    fmt = "{colour} {lithology}"
    answer = '20.00 m of grey sandstone'
    assert interval.summary(fmt=fmt) == answer

    interval_2 = Interval(40, 65, "Red sandstone.", lexicon=lexicon)
    assert interval_2 != interval
    assert interval_2 > interval
    answer = '25.00 m of red sandstone'
    assert max(interval, interval_2).summary(fmt=fmt) == answer

    iv = interval_2 + interval
    assert len(iv.components) == 2
    assert iv.base - iv.top == 45.0

    iv = interval + 5
    assert iv.thickness == 25.0