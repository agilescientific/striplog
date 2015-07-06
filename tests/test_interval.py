# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Interval module.
"""
import pytest

from striplog import Lexicon
from striplog import Interval
from striplog import Component
from striplog.interval import IntervalError

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}


def test_error():
    """ Test the IntervalError.
    """
    lexicon = Lexicon.default()
    interval = Interval(20, 40, "Grey sandstone.", lexicon=lexicon)
    with pytest.raises(IntervalError):
        interval + 'this will raise'


def test_interval():
    """ Test intervals.
    """
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

    rock = Component(r)
    iv = interval + rock
    assert len(iv.components) == 2
