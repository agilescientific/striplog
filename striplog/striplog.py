"""
A striplog is a sequence of intervals.

:copyright: 2019 Agile Geoscience
:license: Apache 2.0
"""
import re
from io import StringIO
import csv
import operator
import warnings
from collections import defaultdict
from collections import OrderedDict
from functools import reduce
from copy import deepcopy

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import requests
import json

from .interval import Interval, IntervalError
from .component import Component
from .legend import Legend
from .canstrat import parse_canstrat
from .markov import Markov_chain
from . import utils
from . import templates


class StriplogError(Exception):
    """
    Generic error class.
    """
    pass


class Striplog(object):
    """
    A Striplog is a sequence of intervals.

    We will build them from LAS files or CSVs.

    Args:
        list_of_Intervals (list): A list of Interval objects.
        source (str): A source for the data. Default None.
        order (str): 'auto', 'depth', 'elevation', or 'none'. Please refer to
            the documentation for details. Best idea is to let the default
            work. Default: 'auto'.
    """
    def __init__(self, list_of_Intervals, source=None, order='auto'):

        list_of_Intervals = deepcopy(list_of_Intervals)

        if not list_of_Intervals:
            m = "Cannot create an empty Striplog."
            raise StriplogError(m)

        if order.lower()[0] == 'a':  # Auto
            # If bases == tops, then this is a bunch of 'points'.
            if all([iv.base.z == iv.top.z for iv in list_of_Intervals]):
                order = 'none'
                self.order = 'none'
            # We will tolerate zero-thickness intervals mixed in.
            elif all([iv.base.z >= iv.top.z for iv in list_of_Intervals]):
                order = 'depth'
                self.order = 'depth'
            elif all([iv.base.z <= iv.top.z for iv in list_of_Intervals]):
                order = 'elevation'
                self.order = 'elevation'
            else:
                m = "Could not determine order from tops and bases."
                raise StriplogError(m)

        if order.lower()[0] == 'n':
            self.order = 'none'
            # Sanity check
            fail = any([iv.base.z != iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "'None' order specified but tops != bases."
                raise StriplogError(m)
            # Order force
            list_of_Intervals.sort(key=operator.attrgetter('top'))

        elif order.lower()[0] == 'd':
            self.order = 'depth'
            # Sanity check
            fail = any([iv.base.z < iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "Depth order specified but base above top."
                raise StriplogError(m)
            # Order force
            list_of_Intervals.sort(key=operator.attrgetter('top'))

        else:
            self.order = 'elevation'
            fail = any([iv.base.z > iv.top.z for iv in list_of_Intervals])
            if fail:
                m = "Elevation order specified but base above top."
                raise StriplogError(m)
            # Order force
            r = True
            list_of_Intervals.sort(key=operator.attrgetter('top'), reverse=r)

        self.source = source

        self.__list = list_of_Intervals
        self.__index = 0  # Set up iterable.

    def __repr__(self):
        length = len(self.__list)
        details = "start={}, stop={}".format(self.start.z, self.stop.z)
        return "Striplog({0} Intervals, {1})".format(length, details)

    def __str__(self):
        s = [str(i) for i in self.__list]
        return '\n'.join(s)

    def __getitem__(self, key):
        if type(key) is slice:
            i = key.indices(len(self.__list))
            result = [self.__list[n] for n in range(*i)]
            if result:
                return Striplog(result)
            else:
                return None
        elif type(key) is list:
            result = []
            for j in key:
                result.append(self.__list[j])
            if result:
                return Striplog(result)
            else:
                return None
        else:
            return self.__list[key]

    def __delitem__(self, key):
        if (type(key) is list) or (type(key) is tuple):
            # Have to compute what the indices *will* be as
            # the initial ones are deleted.
            indices = [x-i for i, x in enumerate(key)]
            for k in indices:
                del self.__list[k]
        else:
            del self.__list[key]
        return

    def __len__(self):
        return len(self.__list)

    def __setitem__(self, key, value):
        if not key:
            return
        try:
            for i, j in enumerate(key):
                self.__list[j] = value[i]
        except TypeError:
            self.__list[key] = value
        except IndexError:
            raise StriplogError("There must be one Interval for each index.")

    def __iter__(self):
        return iter(self.__list)

    def __next__(self):
        """
        Supports iterable.
        """
        try:
            result = self.__list[self.__index]
        except IndexError:
            self.__index = 0
            raise StopIteration
        self.__index += 1
        return result

    def next(self):
        """
        For Python 2 compatibility.
        """
        return self.__next__()

    def __contains__(self, item):
        for r in self.__list:
            if item in r.components:
                return True
        return False

    def __reversed__(self):
        return Striplog(self.__list[::-1])

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = self.__list + other.__list
            return Striplog(result)
        elif isinstance(other, Interval):
            result = self.__list + [other]
            return Striplog(result)
        else:
            raise StriplogError("You can only add striplogs or intervals.")

    def insert(self, index, item):
        if isinstance(item, self.__class__):
            for i, iv in enumerate(item):
                self.__list.insert(index+i, iv)
        elif isinstance(item, Interval):
            self.__list.insert(index, item)
            return
        else:
            raise StriplogError("You can only insert striplogs or intervals.")

    def append(self, item):
        """
        Implements list-like `append()` method.
        """
        if isinstance(item, Interval):
            self.__list.append(item)
            return
        else:
            m = "You can only append an Interval to a Striplog."
            raise StriplogError(m)

    def extend(self, item):
        """
        Implements list-like `extend()` method.
        """
        if isinstance(item, self.__class__):
            self.__list += item
            return
        else:
            m = "You can only extend a Striplog with another Striplog."
            raise StriplogError(m)

    def pop(self, index):
        """
        Implements list-like `pop()` method.
        """
        self.__list.pop(index)

    @property
    def start(self):
        """
        Property. The closest Position to the datum.

        Returns:
            Position.
        """
        if self.order == 'depth':
            # Too naive if intervals can overlap:
            # return self[0].top
            return min(i.top for i in self)
        else:
            return min(i.base for i in self)

    @property
    def stop(self):
        """
        Property. The furthest Position from the datum.

        Returns:
            Position.
        """
        if self.order == 'depth':
            return max(i.base for i in self)
        else:
            return max(i.top for i in self)

    def __sort(self):
        """
        Private method. Sorts into 'natural' order: top-down for depth-ordered
        striplogs; bottom-up for elevation-ordered.

        Sorts in place.

        Returns:
            None.
        """
        self.__list.sort(key=operator.attrgetter('top'))
        return

    def __strict(self):
        """
        Private method. Checks if striplog is monotonically increasing in
        depth.

        Returns:
            Bool.
        """
        def conc(a, b):
            return a + b

        # Check boundaries, b
        b = np.array(reduce(conc, [[i.top.z, i.base.z] for i in self]))

        return all(np.diff(b) >= 0)

    @property
    def cum(self):
        """
        Property. Gives the cumulative thickness of all filled intervals.

        It would be nice to use sum() for this (by defining __radd__),
        but I quite like the ability to add striplogs and get a striplog
        and I don't think we can have both, it's too confusing.

        Not calling it sum, because that's a keyword.

        Returns:
            Float. The cumulative thickness.
        """
        total = 0.0
        for i in self:
            total += i.thickness
        return total

    @property
    def mean(self):
        """
        Property. Returns the mean thickness of all filled intervals.

        Returns:
            Float. The mean average of interval thickness.
        """
        return self.cum / len(self)

    @property
    def components(self):
        """
        Property. Returns the list of compenents in the striplog.

        Returns:
            List. A list of the unique components.
        """
        return [i[0] for i in self.unique if i[0]]

    @property
    def unique(self):
        """
        Property. Summarize a Striplog with some statistics.

        Returns:
            List. A list of (Component, total thickness thickness) tuples.
        """
        all_rx = set([iv.primary for iv in self])
        table = {r: 0 for r in all_rx}
        for iv in self:
            table[iv.primary] += iv.thickness

        return sorted(table.items(), key=operator.itemgetter(1), reverse=True)

    @property
    def top(self):
        """
        Property.
        """
        # For backwards compatibility.
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "Striplog.top is deprecated; please use Striplog.unique"
            warnings.warn(w, DeprecationWarning, stacklevel=2)
        return self.unique

    @classmethod
    def __intervals_from_tops(self,
                              tops,
                              values,
                              basis,
                              components,
                              field=None,
                              ignore_nan=True):
        """
        Private method. Take a sequence of tops in an arbitrary dimension,
        and provide a list of intervals from which a striplog can be made.

        This is only intended to be used by ``from_image()``.

        Args:
            tops (iterable). A list of floats.
            values (iterable). A list of values to look up.
            basis (iterable). A list of components.
            components (iterable). A list of Components.

        Returns:
            List. A list of Intervals.
        """
        # Scale tops to actual depths.
        length = float(basis.size)
        start, stop = basis[0], basis[-1]
        tops = [start + (p/(length-1)) * (stop-start) for p in tops]
        bases = tops[1:] + [stop]

        list_of_Intervals = []
        for i, t in enumerate(tops):

            v, c, d = values[i], [], {}

            if ignore_nan and np.isnan(v):
                continue

            if (field is not None):
                d = {field: v}

            if components is not None:
                try:
                    c = [deepcopy(components[int(v)])]
                except IndexError:
                    c = []

                if c and (c[0] is None):
                    c = []

            interval = Interval(t, bases[i], data=d, components=c)
            list_of_Intervals.append(interval)

        return list_of_Intervals

    @classmethod
    def _clean_longitudinal_data(cls, data, null=None):
        """
        Private function. Make sure we have what we need to make a striplog.
        """

        # Rename 'depth' or 'MD'
        if ('top' not in data.keys()):
            data['top'] = data.pop('depth', data.pop('MD', None))

        # Sort everything
        idx = list(data.keys()).index('top')
        values = sorted(zip(*data.values()), key=lambda x: x[idx])
        data = {k: list(v) for k, v in zip(data.keys(), zip(*values))}

        if data['top'] is None:
            raise StriplogError('Could not get tops.')

        # Get rid of null-like values if specified.
        if null is not None:
            for k, v in data.items():
                data[k] = [i if i != null else None for i in v]

        return data

    @classmethod
    def from_petrel(cls, filename,
                    stop=None,
                    points=False,
                    null=None,
                    function=None,
                    include=None,
                    exclude=None,
                    remap=None,
                    ignore=None):

        """
        Makes a striplog from a Petrel text file.

        Returns:
            striplog.
        """
        result = utils.read_petrel(filename,
                                   function=function,
                                   remap=remap,
                                   )

        data = cls._clean_longitudinal_data(result,
                                            null=null
                                            )

        list_of_Intervals = cls._build_list_of_Intervals(data,
                                                         stop=stop,
                                                         points=points,
                                                         include=include,
                                                         exclude=exclude,
                                                         ignore=ignore
                                                         )
        if list_of_Intervals:
            return cls(list_of_Intervals)
        return None

    @classmethod
    def _build_list_of_Intervals(cls,
                                 data_dict,
                                 stop=None,
                                 points=False,
                                 include=None,
                                 exclude=None,
                                 ignore=None,
                                 lexicon=None):
        """
        Private function. Takes a data dictionary and constructs a list
        of Intervals from it.

        Args:
            data_dict (dict)
            stop (float): Where to end the last interval.
            points (bool)
            include (dict)
            exclude (dict)
            ignore (list)
            lexicon (Lexicon)

        Returns:
            list.
        """

        include = include or {}
        exclude = exclude or {}
        ignore = ignore or []

        # Reassemble as list of dicts
        all_data = []
        for data in zip(*data_dict.values()):
            all_data.append({k: v for k, v in zip(data_dict.keys(), data)})

        # Sort
        all_data = sorted(all_data, key=lambda x: x['top'])

        # Filter down:
        wanted_data = []
        for dictionary in all_data:
            keep = True
            delete = []
            for k, v in dictionary.items():
                incl = include.get(k, utils.null_default(True))
                excl = exclude.get(k, utils.null_default(False))
                if k in ignore:
                    delete.append(k)
                if not incl(v):
                    keep = False
                if excl(v):
                    keep = False
            if delete:
                for key in delete:
                    _ = dictionary.pop(key, None)
            if keep:
                wanted_data.append(dictionary)

        # Fill in
        if not points:
            for i, iv in enumerate(wanted_data):
                if iv.get('base', None) is None:
                    try:  # To set from next interval
                        iv['base'] = wanted_data[i+1]['top']
                    except (IndexError, KeyError):
                        # It's the last interval
                        if stop is not None:
                            thick = stop - iv['top']
                        else:
                            thick = 1
                        iv['base'] = iv['top'] + thick

        # Build the list of intervals to pass to __init__()
        list_of_Intervals = []
        for iv in wanted_data:
            top = iv.pop('top')
            base = iv.pop('base', None)
            descr = iv.pop('description', '')
            if iv:
                c, d = {}, {}
                for k, v in iv.items():
                    match1 = (k[:9].lower() == 'component')
                    match2 = (k[:5].lower() == 'comp ')
                    if match1 or match2:
                        k = re.sub(r'comp(?:onent)? ', '', k, flags=re.I)
                        c[k] = v  # It's a component
                    else:
                        if v is not None:
                            d[k] = v  # It's data
                comp = [Component(c)] if c else None
                this = Interval(**{'top': top,
                                   'base': base,
                                   'description': descr,
                                   'data': d,
                                   'components': comp})
            else:
                this = Interval(**{'top': top,
                                   'base': base,
                                   'description': descr,
                                   'lexicon': lexicon})
            list_of_Intervals.append(this)

        return list_of_Intervals

    @classmethod
    def from_csv(cls, filename=None,
                 text=None,
                 dlm=',',
                 lexicon=None,
                 points=False,
                 include=None,
                 exclude=None,
                 remap=None,
                 function=None,
                 null=None,
                 ignore=None,
                 source=None,
                 stop=None,
                 fieldnames=None):
        """
        Load from a CSV file or text.

        Args
            filename (str): The filename, or use `text`.
            text (str): CSV data as a string, or use `filename`.
            dlm (str): The delimiter, default ','.
            lexicon (Lexicon): The lexicon to use, optional. Only needed if \
                parsing descriptions (e.g. cuttings).
            points (bool): Whether to make a point dataset (as opposed to \
                ordinary intervals with top and base. Default is False.
            include: Default is None.
            exclude: Default is None.
            remap: Default is None.
            function: Default is None.
            null: Default is None.
            ignore: Default is None.
            source: Default is None.
            stop: Default is None.
            fieldnames: Default is None.

        Returns
            Striplog. A new instance.
        """
        if (filename is None) and (text is None):
            raise StriplogError("You must provide a filename or CSV text.")

        if (filename is not None):
            if source is None:
                source = filename
            with open(filename, 'r') as f:
                text = f.read()

        source = source or 'CSV'

        # Deal with multiple spaces in space delimited file.
        if dlm == ' ':
            text = re.sub(r'[ \t]+', ' ', text)

        if fieldnames is not None:
            text = dlm.join(fieldnames) + '\n' + text

        try:
            f = StringIO(text)  # Python 3
        except TypeError:
            f = StringIO(unicode(text))  # Python 2

        reader = csv.DictReader(f, delimiter=dlm)

        # Reorganize the data to make fixing it easier.
        reorg = {k.strip().lower(): []
                 for k in reader.fieldnames
                 if k is not None}
        t = f.tell()
        for key in reorg:
            f.seek(t)
            for r in reader:
                s = {k.strip().lower(): v.strip() for k, v in r.items()}
                try:
                    reorg[key].append(float(s[key]))
                except ValueError:
                    reorg[key].append(s[key])

        f.close()

        remap = remap or {}
        for k, v in remap.items():
            reorg[v] = reorg.pop(k)

        data = cls._clean_longitudinal_data(reorg, null=null)

        list_of_Intervals = cls._build_list_of_Intervals(data,
                                                         points=points,
                                                         lexicon=lexicon,
                                                         include=include,
                                                         exclude=exclude,
                                                         ignore=ignore,
                                                         stop=stop)

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_dict(cls, dictionary):
        """
        Take a dictionary of the form name:depth and return a striplog of
        complete intervals.
        """
        d_sorted = sorted(dictionary.items(), key=lambda i: i[1])
        names = [i[0] for i in d_sorted]
        tops_ = [i[1] for i in d_sorted]
        bases_ = tops_[1:] + [tops_[-1]+1]
        comps_ = [Component({'formation': name}) for name in names]

        list_of_Intervals = []
        for top, base, comp in zip(tops_, bases_, comps_):
            iv = Interval(top=top, base=base, components=[comp])
            list_of_Intervals.append(iv)

        return cls(list_of_Intervals)

    @classmethod
    def from_descriptions(cls, text,
                          lexicon=None,
                          source='CSV',
                          dlm=',',
                          points=False,
                          abbreviations=False,
                          complete=False,
                          order='depth',
                          columns=None,
                          ):
        """
        Convert a CSV string into a striplog. Expects 2 or 3 fields:
            top, description
            OR
            top, base, description

        Args:
            text (str): The input text, given by ``well.other``.
            lexicon (Lexicon): A lexicon, required to extract components.
            source (str): A source. Default: 'CSV'.
            dlm (str): The delimiter, given by ``well.dlm``. Default: ','
            points (bool): Whether to treat as points or as intervals.
            abbreviations (bool): Whether to expand abbreviations in the
                description. Default: False.
            complete (bool): Whether to make 'blank' intervals, or just leave
                gaps. Default: False.
            order (str): The order, 'depth' or 'elevation'. Default: 'depth'.
            columns (tuple or list): The names of the columns.

        Returns:
            Striplog: A ``striplog`` object.

        Example:
            # TOP       BOT        LITH
            312.34,   459.61,    Sandstone
            459.71,   589.61,    Limestone
            589.71,   827.50,    Green shale
            827.60,   1010.84,   Fine sandstone
        """

        text = re.sub(r'(\n+|\r\n|\r)', '\n', text.strip())

        as_strings = []
        try:
            f = StringIO(text)  # Python 3
        except TypeError:
            f = StringIO(unicode(text))  # Python 2
        reader = csv.reader(f, delimiter=dlm, skipinitialspace=True)
        for row in reader:
            as_strings.append(row)
        f.close()

        if not columns:
            if order[0].lower() == 'e':
                columns = ('base', 'top', 'description')
            else:
                columns = ('top', 'base', 'description')

        result = {k: [] for k in columns}

        # Set the indices for the fields.
        tix = columns.index('top')
        bix = columns.index('base')
        dix = columns.index('description')

        for i, row in enumerate(as_strings):

            # THIS ONLY WORKS FOR MISSING TOPS!
            if len(row) == 2:
                row = [row[0], None, row[1]]

            # TOP
            this_top = float(row[tix])

            # THIS ONLY WORKS FOR MISSING TOPS!
            # BASE
            # Base is null: use next top if this isn't the end.
            if row[1] is None:
                if i < len(as_strings)-1:
                    this_base = float(as_strings[i+1][0])  # Next top.
                else:
                    this_base = this_top + 1  # Default to 1 m thick at end.
            else:
                this_base = float(row[bix])

            # DESCRIPTION
            this_descr = row[dix].strip()

            # Deal with making intervals or points...
            if not points:
                # Insert intervals where needed.
                if complete and (i > 0) and (this_top != result['base'][-1]):
                    result['top'].append(result['base'][-1])
                    result['base'].append(this_top)
                    result['description'].append('')
            else:
                this_base = None  # Gets set to Top in striplog creation

            # ASSIGN
            result['top'].append(this_top)
            result['base'].append(this_base)
            result['description'].append(this_descr)

        # Build the list.
        list_of_Intervals = []
        for i, t in enumerate(result['top']):
            b = result['base'][i]
            d = result['description'][i]
            interval = Interval(t, b, description=d,
                                lexicon=lexicon,
                                abbreviations=abbreviations)
            list_of_Intervals.append(interval)

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_image(cls, filename, start, stop, legend,
                   source="Image",
                   col_offset=0.1,
                   row_offset=2,
                   tolerance=0,
                   background=None):
        """
        Read an image and generate Striplog.

        Args:
            filename (str): An image file, preferably high-res PNG.
            start (float or int): The depth at the top of the image.
            stop (float or int): The depth at the bottom of the image.
            legend (Legend): A legend to look up the components in.
            source (str): A source for the data. Default: 'Image'.
            col_offset (Number): The proportion of the way across the image
                from which to extract the pixel column. Default: 0.1 (ie 10%).
            row_offset (int): The number of pixels to skip at the top of
                each change in colour. Default: 2.
            tolerance (float): The Euclidean distance between hex colours,
                which has a maximum (black to white) of 441.67 in base 10.
                Default: 0.
            background (array): A background colour (as hex) to ignore.

        Returns:
            Striplog: The ``striplog`` object.
        """
        if background is None:
            bg = "#xxxxxx"
        else:
            bg = background
        rgb = utils.loglike_from_image(filename, col_offset)
        loglike = np.array([utils.rgb_to_hex(t) for t in rgb if utils.rgb_to_hex(t) != bg])

        # Get the pixels and colour values at 'tops' (i.e. changes).
        tops, hexes = utils.tops_from_loglike(loglike, offset=row_offset)

        # If there are consecutive tops, we assume it's because there is a
        # single-pixel row that we don't want. So take the second one only.
        # We used to do this reduction in ``utils.tops_from_loglike()`` but
        # it was preventing us from making intervals only one sample thick.
        nonconsecutive = np.append(np.diff(tops), 2)
        tops = tops[nonconsecutive > 1]
        hexes = hexes[nonconsecutive > 1]

        # Get the set of unique colours.
        hexes_reduced = list(set(hexes))

        # Get the components corresponding to the colours.
        components = [legend.get_component(h, tolerance=tolerance)
                      for h in hexes_reduced]

        # Turn them into integers.
        values = [hexes_reduced.index(i) for i in hexes]

        basis = np.linspace(start, stop, loglike.size)

        list_of_Intervals = cls.__intervals_from_tops(tops,
                                                      values,
                                                      basis,
                                                      components)

        return cls(list_of_Intervals, source="Image")

    @classmethod
    def from_img(cls, *args, **kwargs):
        """
        For backwards compatibility.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "from_img() is deprecated; please use from_image()"
            warnings.warn(w)
        return cls.from_image(*args, **kwargs)

    @classmethod
    def _from_array(cls, a,
                    lexicon=None,
                    source="",
                    points=False,
                    abbreviations=False):
        """
        DEPRECATING.

        Turn an array-like into a Striplog. It should have the following
        format (where ``base`` is optional):

            [(top, base, description),
             (top, base, description),
             ...
             ]

        Args:
            a (array-like): A list of lists or of tuples, or an array.
            lexicon (Lexicon): A language dictionary to extract structured
                objects from the descriptions.
            source (str): The source of the data. Default: ''.
            points (bool): Whether to treat as point data. Default: False.

        Returns:
            Striplog: The ``striplog`` object.
        """

        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "from_array() is deprecated."
            warnings.warn(w, DeprecationWarning, stacklevel=2)

        csv_text = ''
        for interval in a:
            interval = [str(i) for i in interval]
            if (len(interval) < 2) or (len(interval) > 3):
                raise StriplogError('Elements must have 2 or 3 items')
            descr = interval[-1].strip('" ')
            interval[-1] = '"' + descr + '"'
            csv_text += ', '.join(interval) + '\n'

        return cls.from_descriptions(csv_text,
                                     lexicon,
                                     source=source,
                                     points=points,
                                     abbreviations=abbreviations)

    @classmethod
    def from_log(cls, log,
                 cutoff=None,
                 components=None,
                 legend=None,
                 legend_field=None,
                 field=None,
                 right=False,
                 basis=None,
                 source='Log'):
        """
        Turn a 1D array into a striplog, given a cutoff.

        Args:
            log (array-like): A 1D array or a list of integers.
            cutoff (number or array-like): The log value(s) at which to bin
                the log. Optional.
            components (array-like): A list of components. Use this or
                ``legend``.
            legend (``Legend``): A legend object. Use this or ``components``.
            legend_field ('str'): If you're not trying to match against
                components, then you can match the log values to this field in
                the Decors.
            field (str): The field in the Interval's ``data`` to store the log
                values as.
            right (bool): Which side of the cutoff to send things that are
                equal to, i.e. right on, the cutoff.
            basis (array-like): A depth basis for the log, so striplog knows
                where to put the boundaries.
            source (str): The source of the data. Default 'Log'.

        Returns:
            Striplog: The ``striplog`` object.
        """
        if (components is None) and (legend is None) and (field is None):
            m = 'You must provide a list of components and legend, or a field.'
            raise StriplogError(m)

        if (legend is not None) and (legend_field is None):
            try:  # To treat it like a legend.
                components = [deepcopy(decor.component) for decor in legend]
            except AttributeError:  # It's just a list of components.
                pass

        if legend_field is not None:
            field_values = [getattr(d, legend_field, 0) for d in legend]
            components = [Component() for i in range(int(max(field_values)+1))]
            for i, decor in enumerate(legend):
                components[i] = deepcopy(decor.component)

        if cutoff is not None:

            # First make sure we have enough components.
            try:
                n = len(cutoff)
            except TypeError:
                n = 1
            if len(components) < n+1:
                m = 'For n cutoffs, you need to provide at least'
                m += 'n+1 components.'
                raise StriplogError(m)

            # Digitize.
            try:  # To use cutoff as a list.
                a = np.digitize(log, cutoff, right)
            except ValueError:  # It's just a number.
                a = np.digitize(log, [cutoff], right)

        else:
            a = np.copy(log)

        tops, values = utils.tops_from_loglike(a)

        if basis is None:
            m = 'You must provide a depth or elevation basis.'
            raise StriplogError(m)

        list_of_Intervals = cls.__intervals_from_tops(tops,
                                                      values,
                                                      basis,
                                                      components,
                                                      field=field
                                                      )

        return cls(list_of_Intervals, source=source)

    @classmethod
    def from_las3(cls, string, lexicon=None,
                  source="LAS",
                  dlm=',',
                  abbreviations=False):
        """
        Turn LAS3 'lithology' section into a Striplog.

        Args:
            string (str): A section from an LAS3 file.
            lexicon (Lexicon): The language for conversion to components.
            source (str): A source for the data.
            dlm (str): The delimiter.
            abbreviations (bool): Whether to expand abbreviations.

        Returns:
            Striplog: The ``striplog`` object.

        Note:
            Handles multiple 'Data' sections. It would be smarter for it
            to handle one at a time, and to deal with parsing the multiple
            sections in the Well object.

            Does not read an actual LAS file. Use the Well object for that.
        """
        f = re.DOTALL | re.IGNORECASE
        regex = r'\~\w+?_Data.+?\n(.+?)(?:\n\n+|\n*\~|\n*$)'
        pattern = re.compile(regex, flags=f)
        text = pattern.search(string).group(1)

        s = re.search(r'\.(.+?)\: ?.+?source', string)
        if s:
            source = s.group(1).strip()

        return cls.from_descriptions(text, lexicon,
                                     source=source,
                                     dlm=dlm,
                                     abbreviations=abbreviations)

    @classmethod
    def from_canstrat(cls, filename, source='canstrat'):
        """
        Eat a Canstrat DAT file and make a striplog.
        """
        with open(filename) as f:
            dat = f.read()

        data = parse_canstrat(dat)

        list_of_Intervals = []
        for d in data[7]:  # 7 is the 'card type' for lithology info.
            if d.pop('skip'):
                continue
            top = d.pop('top')
            base = d.pop('base')
            comps = [Component({'lithology': d['rtc'],
                                'colour': d['colour_name']
                                })]
            iv = Interval(top=top, base=base, components=comps, data=d)
            list_of_Intervals.append(iv)

        return cls(list_of_Intervals, source=source)

    def copy(self):
        """Returns a shallow copy."""
        return Striplog([i.copy() for i in self],
                        order=self.order,
                        source=self.source)

    



    # Outputter
    def to_canstrat(self, filename, params):
        """
        Write a Canstrat ASCII file.

        Args:
            filename (str)
            params (dict): The well details. You can use a ``welly`` header
                object.

        Returns:

        """

        return None

    # Outputter
    def to_csv(self,
               filename=None,
               as_text=True,
               use_descriptions=False,
               dlm=",",
               header=True):
        """
        Returns a CSV string built from the summaries of the Intervals.

        Args:
            use_descriptions (bool): Whether to use descriptions instead
                of summaries, if available.
            dlm (str): The delimiter.
            header (bool): Whether to form a header row.

        Returns:
            str: A string of comma-separated values.
        """
        if (filename is None):
            if (not as_text):
                m = "You must provide a filename or set as_text to True."
                raise StriplogError(m)
        else:
            as_text = False

        if as_text:
            output = StringIO()
        else:
            output = open(filename, 'w')

        fieldnames = ['Top', 'Base', 'Component']
        writer = csv.DictWriter(output,
                                delimiter=dlm,
                                fieldnames=fieldnames,
                                quoting=csv.QUOTE_MINIMAL)

        if header:
            writer.writeheader()

        for i in self.__list:
            if use_descriptions and i.description:
                text = i.description
            elif i.primary:
                text = i.primary.summary()
            else:
                text = ''
            d = {j: k for j, k in zip(fieldnames, [i.top.z, i.base.z, text])}
            writer.writerow(d)

        if as_text:
            return output.getvalue()
        else:
            output.close
            return None

    # Outputter
    def to_las3(self, use_descriptions=False, dlm=",", source="Striplog"):
        """
        Returns an LAS 3.0 section string.

        Args:
            use_descriptions (bool): Whether to use descriptions instead
                of summaries, if available.
            dlm (str): The delimiter.
            source (str): The sourse of the data.

        Returns:
            str: A string forming Lithology section of an LAS3 file.
        """
        data = self.to_csv(use_descriptions=use_descriptions,
                           dlm=dlm,
                           header=False)

        return templates.section.format(name='Lithology',
                                        short="LITH",
                                        source=source,
                                        data=data)

    # Outputter
    def to_log(self,
               step=1.0,
               start=None,
               stop=None,
               basis=None,
               field=None,
               field_function=None,
               bins=True,
               dtype='float',
               table=None,
               sort_table=False,
               legend=None,
               legend_field=None,
               match_only=None,
               undefined=0,
               return_meta=False
               ):
        """
        Return a fully sampled log from a striplog. Useful for crossplotting
        with log data, for example.

        Args:
            step (float): The step size. Default: 1.0.
            start (float): The start depth of the new log. You will want to
                match the logs, so use the start depth from the LAS file.
                Default: The basis if provided, else the start of the striplog.
            stop (float): The stop depth of the new log. Use the stop depth
                of the LAS file. Default: The basis if provided, else the stop
                depth of the striplog.
            field (str): If you want the data to come from one of the
                attributes of the components in the striplog, provide it.
            field_function (function): Provide a function to apply to the field
                you are asking for. It's up to you to make sure the function
                does what you want.
            bins (bool): Whether to return the index of the items from the
                lookup table. If False, then the item itself will be returned. 
            dtype (str): The NumPy dtype string for the output log.
            table (list): Provide a look-up table of values if you want. If you
                don't, then it will be constructed from the data.
            sort_table (bool): Whether to sort the table or not. Default: False.
            legend (Legend): If you want the codes to come from a legend,
                provide one. Otherwise the codes come from the log, using
                integers in the order of prevalence. If you use a legend,
                they are assigned in the order of the legend.
            legend_field (str): If you want to get a log representing one of
                the fields in the legend, such as 'width' or 'grainsize'.
            match_only (list): If you only want to match some attributes of
                the Components (e.g. lithology), provide a list of those
                you want to match.
            undefined (number): What to fill in where no value can be
                determined, e.g. ``-999.25`` or ``np.nan``. Default 0.
            return_meta (bool): If ``True``, also return the depth basis
                (np.linspace), and the component table.

        Returns:
            ndarray: If ``return_meta`` was ``True``, you get:

                  * The log data as an array of ints.
                  * The depth basis as an array of floats.
                  * A list of the components in the order matching the ints.

                If ``return_meta`` was ``False`` (the default), you only get
                the log data.
        """
        # Make the preparations.
        if basis is not None:
            start, stop = basis[0], basis[-1]
            step = basis[1] - start
        else:
            start = start or self.start.z
            stop = stop or self.stop.z
            pts = np.ceil((stop - start)/step) + 1
            basis = np.linspace(start, stop, int(pts))

        if (field is not None) or (legend_field is not None):
            result = np.zeros_like(basis, dtype=dtype)
        else:
            result = np.zeros_like(basis, dtype=np.int)

        if np.isnan(undefined):
            try:
                result[:] = np.nan
            except:
                pass  # array type is int

        # If needed, make a look-up table for the log values.
        if table is None:
            if legend:
                table = [j.component for j in legend]
            elif field:
                s = set([iv.data.get(field) for iv in self])
                table = list(filter(None, s))
            else:
                table = [j[0] for j in self.unique]

        # Adjust the table if necessary. Go over all the components in the
        # table list, and remove elements that are not in the match list.
        # Careful! This results in a new table, with components that may not
        # be in the original list of components.
        if match_only is not None:
            if not isinstance(match_only, (list, tuple, set,)):
                raise StriplogError("match_only should be type list not str.")
            table_new = []
            for c in table:
                if c == '':
                    continue  # No idea why sometimes there's a ''
                c_new = Component({k: v for k, v in c.__dict__.items()
                                   if k in match_only})
                # Only add unique, and preserve order.
                if c_new not in table_new:
                    table_new.append(c_new)
            table = table_new
        else:
            match_only = []

        if sort_table:
            table.sort()

        start_ix = self.read_at(start, index=True)
        stop_ix = self.read_at(stop, index=True)
        if stop_ix is not None:
            stop_ix += 1

        # Assign the values.
        for i in self[start_ix:stop_ix]:
            c = i.primary
            if match_only:
                c = Component({k: getattr(c, k, None)
                               for k in match_only})

            if legend and legend_field:  # Use the legend field.
                try:
                    key = legend.getattr(c, legend_field, undefined)
                    key = key or undefined
                except ValueError:
                    key = undefined
            elif field:  # Get data directly from that field in iv.data.
                f = field_function or utils.null
                try:
                    v = f(i.data.get(field, undefined)) or undefined
                    if bins:
                        # Then return the bin we're in...
                        key = (table.index(v) + 1) or undefined
                    else:
                        # ...else return the actual value.
                        key = v
                except ValueError:
                    key = undefined
            else:  # Use the lookup table.
                try:
                    key = (table.index(c) + 1) or undefined
                except ValueError:
                    key = undefined

            top_index = int(np.ceil((max(start, i.top.z)-start)/step))
            base_index = int(np.ceil((min(stop, i.base.z)-start)/step))

            try:
                result[top_index:base_index+1] = key
            except:  # Have a list or array or something.
                result[top_index:base_index+1] = key[0]

        if return_meta:
            return result, basis, table
        else:
            return result

    def to_flag(self, **kwargs):
        """
        A wrapper for ``to_log()`` that returns a boolean array.
        Useful for masking. Has the same interface as ``to_log()``.
        """
        return self.to_log(**kwargs).astype(bool)

    def plot_points(self, ax,
                    legend=None,
                    field=None,
                    field_function=None,
                    undefined=0,
                    **kwargs):
        """
        Plotting, but only for points (as opposed to intervals).
        """

        ys = [iv.top.z for iv in self]

        if field is not None:
            f = field_function or utils.null
            xs = [f(iv.data.get(field, undefined)) for iv in self]
        else:
            xs = [1 for iv in self]

        ax.set_xlim((min(xs), max(xs)))
        for x, y in zip(xs, ys):
            ax.axhline(y, color='lightgray', zorder=0)

        ax.scatter(xs, ys, clip_on=False, **kwargs)

        return ax

    def plot_tops(self, ax, legend=None, field=None, **kwargs):
        """
        Plotting, but only for tops (as opposed to intervals).
        """
        if field is None:
            raise StriplogError('You must provide a field to plot.')

        ys = [iv.top.z for iv in self]

        try:
            try:
                ts = [getattr(iv.primary, field) for iv in self]
            except:
                ts = [iv.data.get(field) for iv in self]
        except:
            raise StriplogError('Could not retrieve field.')

        for y, t in zip(ys, ts):
            ax.axhline(y, color='lightblue', lw=3, zorder=0)
            ax.text(0.1, y-max(ys)/200, t, ha='left')

        return ax

    def plot_field(self, ax, legend=None, field=None, **kwargs):
        """
        Plotting, but only for tops (as opposed to intervals).
        """
        if field is None:
            raise StriplogError('You must provide a field to plot.')

        try:
            try:
                xs = [getattr(iv.primary, field) for iv in self]
            except:
                xs = [iv.data.get(field) for iv in self]
        except:
            raise StriplogError('Could not retrieve field.')

        for iv, x in zip(self.__list, xs):
            _, ymin = utils.axis_transform(ax, 0, iv.base.z, ylim=(self.start.z, self.stop.z), inverse=True)
            _, ymax = utils.axis_transform(ax, 0, iv.top.z, ylim=(self.start.z, self.stop.z), inverse=True)
            ax.axvline(x, ymin=ymin, ymax=ymax)

        return ax

    def max_field(self, field):
        return max(filter(None, [iv.data.get(field) for iv in self]))

    def plot_axis(self,
                  ax,
                  legend,
                  ladder=False,
                  default_width=1,
                  match_only=None,
                  colour=None,
                  colour_function=None,
                  cmap=None,
                  default=None,
                  width_field=None,
                  **kwargs
                  ):
        """
        Plotting, but only the Rectangles. You have to set up the figure.
        Returns a matplotlib axis object.

        Args:
            ax (axis): The matplotlib axis to plot into.
            legend (Legend): The Legend to use for colours, etc.
            ladder (bool): Whether to use widths or not. Default False.
            default_width (int): A width for the plot if not using widths.
                Default 1.
            match_only (list): A list of strings matching the attributes you
                want to compare when plotting.
            colour (str): Which data field to use for colours.
            cmap (cmap): Matplotlib colourmap. Default ``viridis``.
            default (float): The default (null) value.
            width_field (str): The field to use for the width of the patches.
            **kwargs are passed through to matplotlib's ``patches.Rectangle``.

        Returns:
            axis: The matplotlib.pyplot axis.
        """
        default_c = None
        patches = []
        for iv in self.__list:
            origin = (0, iv.top.z)
            d = legend.get_decor(iv.primary, match_only=match_only)
            thick = iv.base.z - iv.top.z

            if ladder:
                if width_field is not None:
                    w = iv.data.get(width_field, 1)
                    w = default_width * w/self.max_field(width_field)
                    default_c = 'gray'
                elif legend is not None:
                    w = d.width or default_width
                    try:
                        w = default_width * w/legend.max_width
                    except:
                        w = default_width
            else:
                w = default_width

            # Allow override of lw
            this_patch_kwargs = kwargs.copy()
            lw = this_patch_kwargs.pop('lw', 0)
            ec = this_patch_kwargs.pop('ec', 'k')
            fc = this_patch_kwargs.pop('fc', None) or default_c or d.colour

            if colour is None:
                rect = mpl.patches.Rectangle(origin,
                                             w,
                                             thick,
                                             fc=fc,
                                             lw=lw,
                                             hatch=d.hatch,
                                             ec=ec,  # edgecolour for hatching
                                             **this_patch_kwargs)
                ax.add_patch(rect)
            else:
                rect = mpl.patches.Rectangle(origin,
                                             w,
                                             thick,
                                             lw=lw,
                                             ec=ec,  # edgecolour for hatching
                                             **this_patch_kwargs)
                patches.append(rect)

        if colour is not None:
            cmap = cmap or 'viridis'
            p = mpl.collections.PatchCollection(patches, cmap=cmap, lw=lw)
            p.set_array(self.get_data(colour,
                                      colour_function,
                                      default=default
                                      ))
            ax.add_collection(p)
            cb = plt.colorbar(p)
            cb.outline.set_linewidth(0)

        return ax

    def get_data(self, field, function=None, default=None):
        """
        Get data from the striplog.
        """
        f = function or utils.null
        data = []
        for iv in self:
            d = iv.data.get(field)
            if d is None:
                if default is not None:
                    d = default
                else:
                    d = np.nan
            data.append(f(d))

        return np.array(data)

    # Outputter
    def plot(self,
             legend=None,
             width=1.5,
             ladder=True,
             aspect=10,
             ticks=(1, 10),
             match_only=None,
             ax=None,
             return_fig=False,
             colour=None,
             cmap='viridis',
             default=None,
             style='intervals',
             field=None,
             label=None,
             **kwargs):
        """
        Hands-free plotting.

        Args:
            legend (Legend): The Legend to use for colours, etc.
            width (int): The width of the plot, in inches. Default 1.
            ladder (bool): Whether to use widths or not. Default False.
            aspect (int): The aspect ratio of the plot. Default 10.
            ticks (int or tuple): The (minor,major) tick interval for depth.
                Only the major interval is labeled. Default (1,10).
            match_only (list): A list of strings matching the attributes you
                want to compare when plotting.
            ax (ax): A maplotlib axis to plot onto. If you pass this, it will
                be returned. Optional.
            return_fig (bool): Whether or not to return the maplotlib ``fig``
                object. Default False.
            colour (str): Which data field to use for colours.
            cmap (cmap): Matplotlib colourmap. Default ``viridis``.
            **kwargs are passed through to matplotlib's ``patches.Rectangle``.

        Returns:
            None. Unless you specify ``return_fig=True`` or pass in an ``ax``.
        """
        if legend is None:
            legend = Legend.random(self.components)

        if style.lower() == 'tops':
            # Make sure width is at least 3 for 'tops' style
            width = max([3, width])

        if ax is None:
            return_ax = False
            fig = plt.figure(figsize=(width, aspect*width))
            ax = fig.add_axes([0.35, 0.05, 0.6, 0.95])
        else:
            return_ax = True

        if (self.order == 'none') or (style.lower() == 'points'):
            # Then this is a set of points.
            ax = self.plot_points(ax=ax, legend=legend, field=field, **kwargs)
        elif style.lower() == 'field':
            if field is None:
                raise StriplogError('You must provide a field to plot.')
            ax = self.plot_field(ax=ax, legend=legend, field=field)
        elif style.lower() == 'tops':
            ax = self.plot_tops(ax=ax, legend=legend, field=field)
            ax.set_xticks([])
        else:
            ax = self.plot_axis(ax=ax,
                                legend=legend,
                                ladder=ladder,
                                default_width=width,
                                match_only=kwargs.get('match_only',
                                                      match_only),
                                colour=colour,
                                cmap=cmap,
                                default=default,
                                width_field=field,
                                **kwargs
                                )

            ax.set_xlim([0, width])
            ax.set_xticks([])

        # Rely on interval order.
        if self.order == 'depth':
            upper, lower = self.start.z, self.stop.z
        else:
            upper, lower = self.stop.z, self.start.z
        rng = abs(upper - lower)

        ax.set_ylim([lower, upper])

        if label is not None:
            for iv in self.__list:
                plt.text(1.6, iv.middle, iv.primary[label], ha='left', va='center', size=10)

        # Make sure ticks is a tuple.
        try:
            ticks = tuple(ticks)
        except TypeError:
            ticks = (1, ticks)

        # Avoid MAXTICKS error.
        while rng/ticks[0] > 250:
            mi, ma = 10*ticks[0], ticks[1]
            if ma <= mi:
                ma = 10 * mi
            ticks = (mi, ma)

        # Carry on plotting...
        minorLocator = mpl.ticker.MultipleLocator(ticks[0])
        ax.yaxis.set_minor_locator(minorLocator)

        majorLocator = mpl.ticker.MultipleLocator(ticks[1])
        majorFormatter = mpl.ticker.FormatStrFormatter('%d')
        ax.yaxis.set_major_locator(majorLocator)
        ax.yaxis.set_major_formatter(majorFormatter)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.get_yaxis().set_tick_params(which='both', direction='out')

        # Optional title.
        title = getattr(self, 'title', None)
        if title is not None:
            ax.set_title(title)

        ax.patch.set_alpha(0)

        if return_ax:
            return ax
        elif return_fig:
            return fig
        else:
            return

    def shift(self, delta=None, start=None):
        """
        Shift all the intervals by `delta` (negative numbers are 'up')
        or by setting a new start depth.

        Returns a copy of the striplog.
        """
        new_strip = self.copy()
        if delta is None:
            if start is None:
                raise StriplogError("You must provide a delta or a new start.")
            delta = start - self.start.z
        for iv in new_strip:
            iv.top = iv.top.z + delta
            iv.base = iv.base.z + delta
        return new_strip

    def read_at(self, d, index=False):
        """
        Get the index of the interval at a particular 'depth' (though this
            might be an elevation or age or anything).

        Args:
            d (Number): The 'depth' to query.
            index (bool): Whether to return the index instead of the interval.

        Returns:
            Interval: The interval, or if ``index==True`` the index of the
                interval, at the specified 'depth', or ``None`` if the depth is
                outside the striplog's range.
        """
        for i, iv in enumerate(self):
            if iv.spans(d):
                return i if index else iv
        return None

    def depth(self, d):
        """
        For backwards compatibility.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            w = "depth() is deprecated; please use read_at()"
            warnings.warn(w)
        return self.read_at(d)

    def extract(self, log, basis, name, function=None):
        """
        'Extract' a log into the components of a striplog.

        Args:
            log (array_like). A log or other 1D data.
            basis (array_like). The depths or elevations of the log samples.
            name (str). The name of the attribute to store in the components.
            function (function). A function that takes an array as the only
                input, and returns whatever you want to store in the 'name'
                attribute of the primary component.

        Returns:
            A copy of the striplog.
        """
        # Build a dict of {index: [log values]} to keep track.
        intervals = {}
        previous_ix = -1
        for i, z in enumerate(basis):
            ix = self.read_at(z, index=True)
            if ix is None:
                continue
            if ix == previous_ix:
                intervals[ix].append(log[i])
            else:
                intervals[ix] = [log[i]]
            previous_ix = ix

        # Set the requested attribute in the primary comp of each interval.
        new_strip = self.copy()
        for ix, data in intervals.items():
            f = function or utils.null
            d = f(np.array(data))
            new_strip[ix].data[name] = d

        return new_strip

    def find(self, search_term, index=False):
        """
        Look for a regex expression in the descriptions of the striplog.
        If there's no description, it looks in the summaries.

        If you pass a Component, then it will search the components, not the
        descriptions or summaries.

        Case insensitive.

        Args:
            search_term (string or Component): The thing you want to search
                for. Strings are treated as regular expressions.
            index (bool): Whether to return the index instead of the interval.

        Returns:
            Striplog: A striplog that contains only the 'hit' Intervals.
                However, if ``index`` was ``True``, then that's what you get.
        """
        hits = []
        for i, iv in enumerate(self):
            try:
                search_text = iv.description or iv.primary.summary()
                pattern = re.compile(search_term, flags=re.IGNORECASE)
                if pattern.search(search_text):
                    hits.append(i)
            except TypeError:
                if search_term in iv.components:
                    hits.append(i)
        if hits and index:
            return hits
        elif hits:
            return self[hits]
        else:
            return

    def __find_incongruities(self, op, index):
        """
        Private method. Finds gaps and overlaps in a striplog. Called by
        find_gaps() and find_overlaps().

        Args:
            op (operator): ``operator.gt`` or ``operator.lt``
            index (bool): If ``True``, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the gaps. A sort of anti-striplog.
        """
        if len(self) == 1:
            return

        hits = []
        intervals = []

        if self.order == 'depth':
            one, two = 'base', 'top'
        else:
            one, two = 'top', 'base'

        for i, iv in enumerate(self[:-1]):
            next_iv = self[i+1]
            if op(getattr(iv, one), getattr(next_iv, two)):
                hits.append(i)

                top = getattr(iv, one)
                base = getattr(next_iv, two)
                iv_gap = Interval(top, base)
                intervals.append(iv_gap)

        if index and hits:
            return hits
        elif intervals:
            return Striplog(intervals)
        else:
            return

    def find_overlaps(self, index=False):
        """
        Find overlaps in a striplog.

        Args:
            index (bool): If True, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the overlaps as intervals.
        """
        return self.__find_incongruities(op=operator.gt, index=index)

    def find_gaps(self, index=False):
        """
        Finds gaps in a striplog.

        Args:
            index (bool): If True, returns indices of intervals with
            gaps after them.

        Returns:
            Striplog: A striplog of all the gaps. A sort of anti-striplog.
        """
        return self.__find_incongruities(op=operator.lt, index=index)

    def prune(self, limit=None, n=None, percentile=None, keep_ends=False):
        """
        Remove intervals below a certain limit thickness. In place.

        Args:
            limit (float): Anything thinner than this will be pruned.
            n (int): The n thinnest beds will be pruned.
            percentile (float): The thinnest specified percentile will be
                pruned.
            keep_ends (bool): Whether to keep the first and last, regardless
                of whether they meet the pruning criteria.
        """
        strip = self.copy()

        if not (limit or n or percentile):
            m = "You must provide a limit or n or percentile for pruning."
            raise StriplogError(m)
        if limit:
            prune = [i for i, iv in enumerate(strip) if iv.thickness < limit]
        if n:
            prune = strip.thinnest(n=n, index=True)
        if percentile:
            n = np.floor(len(strip)*percentile/100)
            prune = strip.thinnest(n=n, index=True)

        if keep_ends:
            first, last = 0, len(strip) - 1
            if first in prune:
                prune.remove(first)
            if last in prune:
                prune.remove(last)

        del strip[prune]

        return strip

    def anneal(self, mode='middle'):
        """
        Fill in empty intervals by growing from top and base.

        Note that this operation happens in-place and destroys any information
        about the ``Position`` (e.g. metadata associated with the top or base).
        See GitHub issue #54.

        If there are overlaps in your striplog, then this method may have
        unexpected results.

        Args
            mode (str): One of ['down', 'middle', 'up']. Which way to 'flood'
                into the gaps.

        Returns
            Striplog. A new instance of the Striplog class.
        """
        strip = deepcopy(self)

        gaps = strip.find_gaps(index=True)

        if not gaps:
            return

        for gap in gaps:
            before = strip[gap]
            after = strip[gap + 1]

            if mode == 'middle':
                if strip.order == 'depth':
                    t = (after.top.z-before.base.z)/2
                    before.base = before.base.z + t
                    after.top = after.top.z - t
                else:
                    t = (after.base-before.top)/2
                    before.top = before.top.z + t
                    after.base = after.base.z - t

            elif mode == 'down':
                if strip.order == 'depth':
                    before.base = after.top.z
                else:
                    before.top = after.base.z

            elif mode == 'up':
                if strip.order == 'depth':
                    after.top = before.base.z
                else:
                    after.base = before.top.z

        return strip

    def fill(self, component=None):
        """
        Fill gaps with the component provided.

        Example
            t = s.fill(Component({'lithology': 'cheese'}))
        """
        c = [component] if component is not None else []

        # Make the intervals to go in the gaps.
        gaps = self.find_gaps()
        if not gaps:
            return self
        for iv in gaps:
            iv.components = c

        return deepcopy(self) + gaps

    def union(self, other):
        """
        Makes a striplog of all unions.

        Args:
            Striplog. The striplog instance to union with.

        Returns:
            Striplog. The result of the union.
        """
        if not isinstance(other, self.__class__):
            m = "You can only union striplogs with each other."
            raise StriplogError(m)

        result = []
        for iv in deepcopy(self):
            for jv in other:
                if iv.any_overlaps(jv):
                    iv = iv.union(jv)
            result.append(iv)
        return Striplog(result)

    def intersect(self, other):
        """
        Makes a striplog of all intersections.

        Args:
            Striplog. The striplog instance to intersect with.

        Returns:
            Striplog. The result of the intersection.
        """
        if not isinstance(other, self.__class__):
            m = "You can only intersect striplogs with each other."
            raise StriplogError(m)

        result = []
        for iv in self:
            for jv in other:
                try:
                    result.append(iv.intersect(jv))
                except IntervalError:
                    # The intervals don't overlap
                    pass
        return Striplog(result)

    def merge_overlaps(self):
        """
        Merges overlaps by merging overlapping Intervals.

        The function takes no arguments and returns ``None``. It operates on
        the striplog 'in place'

        TODO: This function will not work if any interval overlaps more than
            one other intervals at either its base or top.
        """
        overlaps = np.array(self.find_overlaps(index=True))

        if not overlaps.any():
            return

        for overlap in overlaps:
            before = self[overlap].copy()
            after = self[overlap + 1].copy()

            # Get rid of the before and after pieces.
            del self[overlap]
            del self[overlap]

            # Make the new piece.
            new_segment = before.merge(after)

            # Insert it.
            self.insert(overlap, new_segment)

            overlaps += 1

        return

    def merge_neighbours(self, strict=True):
        """
        Makes a new striplog in which matching neighbours (for which the
        components are the same) are unioned. That is, they are replaced by
        a new Interval with the same top as the uppermost and the same bottom
        as the lowermost.

        Args
            strict (bool): If True, then all of the components must match.
                If False, then only the primary must match.

        Returns:
            Striplog. A new striplog.

        TODO:
            Might need to be tweaked to deal with 'binary striplogs' if those
            aren't implemented with components.
        """
        new_strip = [self[0].copy()]

        for lower in self[1:]:

            # Determine if touching.
            touching = new_strip[-1].touches(lower)

            # Decide if match.
            if strict:
                similar = new_strip[-1].components == lower.components
            else:
                similar = new_strip[-1].primary == lower.primary

            # Union if both criteria met.
            if touching and similar:
                new_strip[-1] = new_strip[-1].union(lower)
            else:
                new_strip.append(lower.copy())

        return Striplog(new_strip)

    def thickest(self, n=1, index=False):
        """
        Returns the thickest interval(s) as a striplog.

        Args:
            n (int): The number of thickest intervals to return. Default: 1.
            index (bool): If True, only the indices of the intervals are
                returned. You can use this to index into the striplog.

        Returns:
            Interval. The thickest interval. Or, if ``index`` was ``True``,
            the index of the thickest interval.
        """
        s = sorted(range(len(self)), key=lambda k: self[k].thickness)
        indices = s[-n:]
        if index:
            return indices
        else:
            if n == 1:
                # Then return an interval.
                i = indices[0]
                return self[i]
            else:
                return self[indices]

    def thinnest(self, n=1, index=False):
        """
        Returns the thinnest interval(s) as a striplog.

        Args:
            n (int): The number of thickest intervals to return. Default: 1.
            index (bool): If True, only the indices of the intervals are
                returned. You can use this to index into the striplog.

        Returns:
            Interval. The thickest interval. Or, if ``index`` was ``True``,
            the index of the thickest interval.

        TODO:
            If you ask for the thinnest bed and there's a tie, you will
            get the last in the ordered list.
        """
        s = sorted(range(len(self)), key=lambda k: self[k].thickness)
        indices = s[:n]
        if index:
            return indices
        else:
            if n == 1:
                i = indices[0]
                return self[i]
            else:
                return self[indices]

    def hist(self,
            lumping=None,
            summary=False,
            sort=True,
            plot=True,
            legend=None,
            ax=None,
            rotation=0,
            ha='center',
            ):
        """
        Plots a histogram and returns the data for it.

        Args:
            lumping (str): If given, the bins will be lumped based on this
                attribute of the primary components of the intervals
                encountered.
            summary (bool): If True, the summaries of the components are
                returned as the bins. Otherwise, the default behaviour is to
                return the Components themselves.
            sort (bool): If True (default), the histogram is sorted by value,
                starting with the largest.
            plot (bool): If True (default), produce a bar plot.
            legend (Legend): The legend with which to colour the bars.
            ax (axis): An axis object, which will be returned if provided.
                If you don't provide one, it will be created but not returned.
            rotation (int): The rotation angle of the x-axis tick labels.
                Default is 0 but -45 is useful.
            ha (str): The horizontal alignment of the x-axis tick labels.
                Default is 'center' but 'left' is good for -ve rotation.

        Returns:
            Tuple: A tuple of tuples of entities and counts.

        TODO:
            Deal with numeric properties, so I can histogram 'Vp' values, say.
        """
        # This seems like overkill, but collecting all this stuff gives
        # the user some choice about what they get back.
        entries = OrderedDict()
        for i in self:
            if lumping:
                k = i.primary[lumping]
            else:
                if summary:
                    k = i.primary.summary()
                else:
                    k = i.primary
            v = entries.get(k, {'thick': 0}).get('thick', 0)
            
            entries[k] = {
                        'label': i.primary.summary(),
                        'colour': legend.get_colour(i.primary) if legend else None,
                        'thick': v + i.thickness,
                        }

        if sort:
            allitems = sorted(entries.items(),
                            key=lambda i: i[1]['thick'],
                            reverse=True
                            )
            ents, data = zip(*allitems)
        else:
            ents, data = tuple(entries.keys()), tuple(entries.values())
            
        counts = [d['thick'] for d in data]

        # Make plot.
        if plot:
            if ax is None:
                fig, ax = plt.subplots()
                return_ax = False
            else:
                return_ax = True

            ind = np.arange(len(ents))
            bars = ax.bar(ind, counts, align='center')
            ax.set_xticks(ind)
            ax.set_xticklabels([d['label'] for d in data],
                            rotation=rotation,
                            ha=ha)
            if legend:
                colours = [d['colour'] for d in data]
                for b, c in zip(bars, colours):
                    b.set_color(c)
            ax.set_ylabel('Thickness [m]')
        else:
            bars = []

        if plot and return_ax:
            return counts, ents, ax

        return counts, ents, bars

    histogram = hist

    def bar(self, height='thickness', sort=False, reverse=False,
            legend=None, ax=None, figsize=None, **kwargs):
        """
        Make a bar plot of thickness per interval.

        Args:
            height (str): The property of the primary component to plot.
            sort (bool or function): Either pass a boolean indicating whether
                to reverse sort by thickness, or pass a function to be used as
                the sort key.
            reverse (bool): Reverses the sort order.
            legend (Legend): The legend to plot with.
            ax (axis): Optional axis to plot to.
            figsize (tuple): A figure size, (width, height), optional.
            **kwargs: passed to the matplotlib bar plot command, ax.bar().

        Returns:
            axis: If you sent an axis in, you get it back.
        """
        if sort:
            if sort is True:
                def func(x): return x.thickness
                reverse = True
            data = sorted(self, key=func, reverse=reverse)
        else:
            data = self[:]

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        heights = [getattr(i, height) for i in data]

        comps = [i[0] for i in self.unique]

        if legend is None:
            legend = Legend.random(comps)

        colors = [legend.get_colour(i.primary) for i in data]

        bars = ax.bar(range(len(data)), height=heights, color=colors, **kwargs)

        # Legend.
        colourables = [i.primary.summary() for i in data]
        unique_bars = dict(zip(colourables, bars))
        ax.legend(list(unique_bars.values()), list(unique_bars.keys()))

        ax.set_ylabel(height.title())

        return ax

    def invert(self, copy=False):
        """
        Inverts the striplog, changing its order and the order of its contents.

        Operates in place by default.

        Args:
            copy (bool): Whether to operate in place or make a copy.

        Returns:
            None if operating in-place, or an inverted copy of the striplog
                if not.
        """
        if copy:
            return Striplog([i.invert(copy=True) for i in self])
        else:
            for i in self:
                i.invert()
            self.__sort()
            o = self.order
            self.order = {'depth': 'elevation', 'elevation': 'depth'}[o]
            return

    def crop(self, extent, copy=False):
        """
        Crop to a new depth range.

        Args:
            extent (tuple): The new start and stop depth. Must be 'inside'
                existing striplog.
            copy (bool): Whether to operate in place or make a copy.

        Returns:
            Operates in place by deault; if copy is True, returns a striplog.
        """
        try:
            if extent[0] is None:
                extent = (self.start.z, extent[1])
            if extent[1] is None:
                extent = (extent[0], self.stop.z)
        except:
            m = "You must provide a 2-tuple for the new extents. Use None for"
            m += " the existing start or stop."
            raise StriplogError(m)

        first_ix = self.read_at(extent[0], index=True)
        last_ix = self.read_at(extent[1], index=True)

        first = self[first_ix].split_at(extent[0])[1]
        last = self[last_ix].split_at(extent[1])[0]

        new_list = self.__list[first_ix:last_ix+1].copy()
        new_list[0] = first
        new_list[-1] = last

        if copy:
            return Striplog(new_list)
        else:
            self.__list = new_list
            return

    def net_to_gross(strip, attr):
        """
        Compute the ratio of intervals having that attribute as `True` to the
        total thickness.

        TODO
            Allow user to give a cut-off value to apply to the attribute,
            if it's a continuous scalar and not boolean.

        Args
            attr (str): Which attribute to use. Must have boolean values.

        Returns
            float. The net:gross ratio.
        """
        net = non = 0
        for c, x in strip.unique:
            if getattr(c, attr):
                net = x
            else:
                non = x
        return net / (net + non)

    def quality(self, tests, alias=None):
        """
        Run a series of tests and return the corresponding results.

        Based on curve testing for ``welly``.

        Args:
            tests (list): a list of functions.

        Returns:
            list. The results. Stick to booleans (True = pass) or ints.
        """
        # This is hacky... striplog should probably merge with welly...

        # Ignore aliases
        alias = alias or {}
        alias = alias.get('striplog', alias.get('Striplog', []))

        # Gather the tests.
        # First, anything called 'all', 'All', or 'ALL'.
        # Second, anything with the name of the curve we're in now.
        # Third, anything that the alias list has for this curve.
        # (This requires a reverse look-up so it's a bit messy.)
        this_tests =\
            tests.get('all', [])+tests.get('All', [])+tests.get('ALL', [])\
            + tests.get('striplog', tests.get('Striplog', []))\
            + utils.flatten_list([tests.get(a) for a in alias])
        this_tests = filter(None, this_tests)

        # If we explicitly set zero tests for a particular key, then this
        # overrides the 'all' tests.
        if not tests.get('striplog', tests.get('Striplog', 1)):
            this_tests = []

        return {test.__name__: test(self) for test in this_tests}

    @property
    def _table(self):
        """
        A table (list of tuples) of the tops and bases we encounter, starting
        at the top. We will need to know 3 things: whether it's a top or a
        base, the depth it's at, and which interval in the striplog it
        corresponds to.
        """
        table = []
        for i, interval in enumerate(self):
            table.append(('T', interval.top.middle, i))
            table.append(('B', interval.base.middle, i))
        table = sorted(table, key=lambda x: x[1])
        return table

    def _merge_table(self, attr, reverse=False):
        """
        Do the merge operation on a table, and return a new table with
        no nesting / overlaps.

        Args
            attr (str): The attribute of the component you want to use. You
                must provide an attribute.
            reverse (bool): Whether to reverse the condition.

        Returns
            list: The merged table.
        """
        merged, stack = [], []
        op = operator.le if reverse else operator.ge

        for interface in self._table:

            tb, depth, idx = interface

            if stack:
                # 'this' is the top or base we're on in this loop iteration.
                try:
                    this = getattr(self[idx], attr)
                except AttributeError:
                    this = getattr(self[idx].primary, attr)

                # 'current' is the highest priority unit in the stack.
                try:
                    current = getattr(self[stack[-1]], attr)
                except AttributeError:
                    current = getattr(self[stack[-1]].primary, attr)

                # Compare 'this' to 'current' to decide what to do.
                merge = op(this, current)
            else:
                merge = True

            if tb == 'T':

                # If this one meets the condition, merge it.
                if merge:
                    # End the current unit, if any.
                    if stack:
                        merged.append(('B', depth, stack[-1]))
                    # Start the new top.
                    merged.append(interface)

                # Insert this unit into stack and re-sort.
                # (This is easier than trying to insert in the right place.)
                stack.append(idx)
                try:
                    stack = sorted(stack,
                                   key=lambda i: getattr(self[i], attr),
                                   reverse=reverse)
                except AttributeError:
                    stack = sorted(stack,
                                   key=lambda i: getattr(self[i].primary, attr),
                                   reverse=reverse)

            elif tb == 'B':
                have_merged = False

                # If this is the current unit's base, append it to the merge.
                if idx == stack[-1]:
                    merged.append(interface)
                    have_merged = True

                # End this unit in the stack.
                stack.remove(idx)

                # Add a top for the new current unit, if any, but only if we
                # did a merge.
                if stack and have_merged:
                    merged.append(('T', depth, stack[-1]))

        return merged

    def _striplog_from_merge_table(self, table):
        """
        Make a merge table into a Striplog instance.

        Args
            table (list). The table of tops and bases, represented as tuples.

        Returns
            Striplog. A new Striplog instance.
        """
        m = []
        for top, bot in zip(table[::2], table[1::2]):

            # If zero thickness, discard.
            if top[1] == bot[1]:
                continue

            i = self[top[2]].copy()
            i.top = top[1]
            i.base = bot[1]
            m.append(i)

        return Striplog(m)

    def merge(self, attr, reverse=False):
        """
        Merge the intervals in a striplog, using an attribute of the primary
        component for priority ordering.

        Args
            attr (str): The attribute of the component you want to use. You \
                must provide an attribute.
            reverse (bool): Whether to reverse the condition.

        Returns
            Striplog: The merged striplog.
        """
        m = self._merge_table(attr, reverse=reverse)
        return self._striplog_from_merge_table(m)

    def is_binary(self, attr=None):
        """
        Determine if `attr`, which must be an attribute of every primary
        component, allows this striplog to be interpreted as a binary striplog.
        If no `attr` is provided, the first attribute of the primary comp-
        onent is used.
        """
        try:
            primaries = [getattr(i.primary, attr) for i in self]
        except:
            primaries = [list(i.primary.__dict__.values())[0] for i in self]
        return all(map(lambda x: isinstance(x, bool), primaries))

    def to_binary_log(self, attr, step):
        """
        Adaptation of `to_log` but deals with binary attributes of striplogs.

        Args
            attr (str): Which attribute to make into a log.
        """
        log, basis, comps = self.to_log(step=step,
                                        match_only=[attr],
                                        undefined=-1,
                                        return_meta=True)
        if -1 in log:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                w = "We have undefined values, there might be a problem."
                warnings.warn(w)
        return log - 1, basis, comps

    def binary_morphology(self, attr, operation, step=1.0, p=3):
        """
        Perform a discrete binary morphology operation on the striplog.

        Args
            attr (str): The attribute to use for the filtering. Must have
                boolean values.
            operation (str): One of `erosion`, `dilation`, `opening` or
                `closing`.
            step (float): The step size to use in discretization. Default is
                1 but you might want to use something smaller, e.g. 0.1.
            p (int): The length of the structuring element, in samples (not
                natual units). Odd numbers are symmetrical and more intuitive.
                Default is 3.

        Returns
            Striplog. A new striplog instance.
        """
        ops = {
            'erosion': utils.binary_erosion,
            'dilation': utils.binary_dilation,
            'opening': utils.binary_opening,
            'closing': utils.binary_closing,
        }
        if not self.is_binary():
            print("Cannot interpret striplog as binary.")
        log, basis, comps = self.to_binary_log(step=step, attr=attr)
        proc = ops[operation](log, p)
        if operation == 'closing':
            proc = proc | log

        return Striplog.from_log(proc, components=comps, basis=basis)

    @classmethod
    def from_macrostrat(cls, lng, lat, buffer_size=0.2):
        """
        Create a striplog from components derived using the MacroStrat API.
            This is simply a helper function to make things easier, but it
            works because we know what our data looks like in advance.

        Note: In order to plot this, you will need to add space for text and 
            other decoration. This simply gives a Striplog back which _can_
            be plotted.

        Args:
            components (list):

        Returns:
            Tuple of:
                strip (striplog.Striplog)
                legend (striplog.Legend)

        Example:
        lng = -64.3573186
        lat = 44.4454632
        buffer_size = 0.3
        striplog.striplog.from_macrostrat(lng, lat, buffer_size)
        {'top': Position({'middle': 358.9, 'units': 'm'}), 
            'base': Position({'middle': 419.2, 'units': 'm'}), 
            'description': '', 'data': {}, 'components': [Component({
                'map_id': 948660.0, 'scale': 'small', 'source_id': 7.0,
                'name': 'Devonian plutonic: undivided granitic rocks',
                'age': 'devonian', 'lith': 'plutonic: undivided granitic rocks',
                'best_age_top': 358.9, 'best_age_bottom': 419.2, 't_int': 94.0,
                'b_int': 94.0, 'color': '#cb8c37', 'source': 'MacroStrat.org (CC-BY)})]}
        {'top': Position({'middle': 358.9, 'units': 'm'}),
            'base': Position({'middle': 541.0, 'units': 'm'}),
            'description': '', 'data': {}, 'components': [Component({
                'map_id': 948228.0, 'scale': 'small', 'source_id': 7.0,
                'name': 'Cambrian-Devonian sedimentary', 'age': 'cambrian-devonian',
                'lith': 'sedimentary', 'best_age_top': 358.9, 'best_age_bottom': 541.0,
                't_int': 94.0, 'b_int': 122.0, 'color': '#99c08d',
                'source': 'MacroStrat.org (CC-BY)})]}
        {'top': Position({'middle': 443.8, 'units': 'm'}),
            'base': Position({'middle': 541.0, 'units': 'm'}),
            'description': '', 'data': {}, 'components': [Component({
                'map_id': 973359.0, 'scale': 'small', 'source_id': 7.0,
                'name': 'Cambrian-Ordovician sedimentary', 'age': 'cambrian-ordovician',
                'lith': 'sedimentary', 'best_age_top': 443.8, 'best_age_bottom': 541.0,
                't_int': 112.0, 'b_int': 122.0, 'color': '#409963',
                'source': 'MacroStrat.org (CC-BY)})]}
        """
        # Get the 
        features = utils.geology_from_macrostrat(lng=lng, lat=lat,
                                                 buffer_size=buffer_size)

        columns = ('color', 'lith', 'age')

        intervals = []

        for feature in features:
            if feature['geometry'] is None:
                continue

            components = []
            for lith in utils.get_liths_from_macrostrat(feature['properties']['lith']):
                c = Component({'lithology': lith})
                components.append(c)

            intervals.append(Interval(
                            top=feature['properties']['best_age_top'],
                            base=feature['properties']['best_age_bottom'],
                            components=components,
                            description=feature['properties']['descrip'])
                            )

        return cls(intervals, source='Macrostrat [CC-BY]', order='age')
