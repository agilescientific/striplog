"""
Defines positions, eg for top and base of an interval.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
from functools import total_ordering


class PositionError(Exception):
    """
    Generic error class.
    """
    pass


class Meta(object):
    """
    Used for metadata.
    """
    def __init__(self, meta):
        for k, v in meta.items():
            if k and v:
                setattr(self, k, v)


@total_ordering
class Position(object):
    """
    Used to represent a position: a top or base.

    Not sure whether to go with upper-middle-lower or z_max, z_mid, z_min.
    Sticking to upper and lower, because ordering in Intervals is already
    based on 'above' and 'below'.
    """
    def __init__(self,
                 middle=None,
                 upper=None, lower=None,
                 x=None, y=None,
                 units='m',
                 meta=None):

        if middle is None:
            if not (upper and lower):
                m = "You must provide middle, or upper and lower."
                raise PositionError(m)
        else:
            self.middle = float(middle)

        if upper is not None:
            self.upper = float(upper)
        else:
            self.upper = self.middle

        if lower is not None:
            self.lower = float(lower)
        else:
            self.lower = self.middle

        if x is not None:
            if y is None:
                raise PositionError("You must provide x and y.")
            else:
                self.x, self.y = x, y

        self.units = units

        if meta is not None:
            self.meta = Meta(meta)

    def __str__(self):
        """
        A bit of a hack. May want to re-think duplicating things, as
        opposed to just delaing with empty attributes.
        """
        temp = self.__dict__.copy()
        if getattr(self, 'middle', None):
            if temp['upper'] == temp['middle']:
                del temp['upper']
            if temp['lower'] == temp['middle']:
                del temp['lower']
        return temp.__str__()

    def __repr__(self):
        s = str(self)
        return "Position({0})".format(s)

    def __eq__(self, other):
        """
        Must supply __eq__ and one other rich comparison for
        the total_ordering function to provide the others.
        """
        if isinstance(other, self.__class__):
            return self.middle == other.middle

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.middle < other.middle

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        items = ['upper', 'middle', 'lower']
        rows = ''
        row = '<tr><td><strong>{e}</strong></td><td>{v}</td></tr>'
        for i, e in enumerate(items):
            v = getattr(self, e, '')
            rows += row.format(e=e, v=v)

        html = '<table>{}</table>'.format(rows)
        return html

    @property
    def z(self):
        """
        Property. Guaranteed to give the 'middle' depth, either as defined,
        or the average of the upper and lower bounds.
        """
        return self.__dict__.get('middle', (self.upper + self.lower)/2)

    @property
    def uncertainty(self):
        """
        Property. The range of the upper and lower bounds.
        """
        return abs(self.upper - self.lower)

    @property
    def span(self):
        """
        Property. A tuple of lower, upper. Provided for convenience.
        """
        return self.lower, self.upper

    def invert(self):
        """
        Inverts upper and lower in place.
        """
        old_lower = self.lower
        self.lower = self.upper
        self.upper = old_lower
        return
