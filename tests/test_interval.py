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
        error = interval + 'this will raise'
        assert error


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
    answer = '20.00 m of grey sandstone'
    # Max gives uppermost
    assert max(interval, interval_2).summary(fmt=fmt) == answer

    iv = interval_2 + interval
    assert len(iv.components) == 2
    assert iv.base.z - iv.top.z == 45.0

    rock = Component(r)
    iv = interval + rock
    assert len(iv.components) == 2


def test_interval_html():
    """For jupyter notebook
    """
    interval = Interval(10, 20, components=[Component(r)])
    html_start = '<table><tr><td style="width:2em; background-color:#DDDDDD" rowspan="6"></td><td><strong>top</strong></td><td>10.0</td></tr><tr><td><strong>primary</strong></td><td><table><tr><td><strong>'
    # Can't test all of it because the component attributes are given in
    # random order.
    assert interval._repr_html_()[:187] == html_start

# Depth ordered
i1 = Interval(top=61, base=62.5, components=[Component({'lithology': 'limestone'})])
i2 = Interval(top=62, base=63, components=[Component({'lithology': 'sandstone'})])
i3 = Interval(top=62.5, base=63.5, components=[Component({'lithology': 'siltstone'})])
i4 = Interval(top=63, base=64, components=[Component({'lithology': 'shale'})])
i5 = Interval(top=63.1, base=63.4, components=[Component({'lithology': 'dolomite'})])

# Elevation ordered
i8 = Interval(top=200, base=100, components=[Component({'lithology': 'sandstone'})])
i7 = Interval(top=150, base=50, components=[Component({'lithology': 'limestone'})])
i6 = Interval(top=100, base=0, components=[Component({'lithology': 'siltstone'})])


def test_interval_invert():
    """Test inverting works.
    """
    i = i1.invert(copy=True)
    assert i.order == 'elevation'
    ii = i2.invert()
    assert ii is None
    assert i2.order == 'elevation'
    i2.invert()


def test_interval_binary_relationships():
    """ Test the binary relationships.
    """
    assert i3 != i2
    assert i2 > i4 > i5
    assert min(i1, i2, i5).summary() == "0.30 m of dolomite"
    iv = i2 + i3
    assert iv.thickness == 1.5

    assert i6.relationship(i7) == 'partially'
    assert i5.relationship(i4) == 'containedby'

    assert i1.partially_overlaps(i2)
    assert i2.partially_overlaps(i3)
    assert not i2.partially_overlaps(i4)
    assert i6.partially_overlaps(i7)
    assert i7.partially_overlaps(i6)
    assert not i6.partially_overlaps(i8)
    assert i5.is_contained_by(i3)
    assert i5.is_contained_by(i4)
    assert not i5.is_contained_by(i2)


def test_interval_binary_operations():
    """ Test the binary operations.
    """
    assert '40.0%' in i1.union(i3).description
    assert len(i3.difference(i5)) == 2
    assert i1.intersect(i2, blend=False).description == ''

    x = i4.merge(i5)
    x[-1].base = 65
    assert len(x) == 3
    assert x.stop.z == 65.0


def test_interval_binary_errors():
    """Test errors thrown by binary operations.
    """
    with pytest.raises(IntervalError):
        i1.merge(i8)
    with pytest.raises(IntervalError):
        i1.merge(i4)
    with pytest.raises(IntervalError):
        i1.intersect(i4)
