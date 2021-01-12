"""
Defines a legend for displaying components.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
# from builtins import object
from io import StringIO
import csv
import warnings
import random
import re
import itertools

try:
    from functools import partialmethod
except:  # Python 2
    from utils import partialmethod

import numpy as np
from matplotlib import patches
import matplotlib.pyplot as plt

from .component import Component
from . import utils
from .defaults import LEGEND__NSDOE
from .defaults import LEGEND__Canstrat
from .defaults import LEGEND__NAGMDM__6_2
from .defaults import LEGEND__NAGMDM__6_1
from .defaults import LEGEND__NAGMDM__4_3
from .defaults import LEGEND__SGMC
from .defaults import TIMESCALE__ISC
from .defaults import TIMESCALE__USGS_ISC
from .defaults import TIMESCALE__DNAG

###############################################
# This module is not used directly, but must
# be imported in order to register new hatches.
from . import hatches  # DO NOT DELETE
###############################################


class LegendError(Exception):
    """
    Generic error class.
    """
    pass


class Decor(object):
    """
    A single display style. A Decor describes how to display a given set
    of Component properties.

    In general, you will not usually use a Decor on its own. Instead, you
    will want to use a Legend, which is just a list of Decors, and leave
    the Decors to the Legend.

    Args:
      params (dict): The parameters you want in the Decor. There must be a
        Component to attach the decoration to, and at least 1 other attribute.
        It's completely up to you, but you probably want at least a colour
        (hex names like #AAA or #d3d3d3, or matplotlib's English-language
        names listed at http://ageo.co/modelrcolour are acceptable.

        The only other parameter the class recognizes for now is 'width',
        which is the width of the striplog element.

    Example:
      my_rock = Component({ ... })
      d = {'component': my_rock, 'colour': 'red'}
      my_decor = Decor(d)
    """
    def __init__(self, *params, **kwargs):
        """
        Supports the passing in of a single dictionary, or the passing of
        keyword arguments.

        Possibly a bad idea; review later.
        """
        for p in params:
            params = p
        for k, v in kwargs.items() or params.items():
            k = k.lower().replace(' ', '_')
            if k in ['colour', 'color']:
                k = 'colour'
                if not v:
                    v = '#eeeeee'
            try:
                v = v.lower()
            except AttributeError:
                v = v
            setattr(self, k, v)

        if (getattr(self, 'component', None) is None) and (getattr(self, 'curve', None) is None):
            raise LegendError("You must provide a Component to decorate.")

        if len(self.__dict__) < 2:
            raise LegendError("You must provide at least one decoration.")

        # Make sure we have a width, and it's a float, even if it's None.
        try:
            self.width = float(getattr(self, 'width', None))
        except (TypeError, ValueError):
            self.width = None

        # Make sure we have a hatch, even if it's None. And correct 'none's.
        self.hatch = getattr(self, 'hatch', None)
        if self.hatch == 'none':
            self.hatch = None

    def __repr__(self):
        s = repr(self.__dict__)
        return "Decor({0})".format(s)

    def __str__(self):
        s = str(self.__dict__)
        return "Decor({0})".format(s)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = [self, other]
            return Legend(result)
        elif isinstance(other, Legend):
            return other + self
        else:
            raise LegendError("You can only add legends or decors.")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        # Weed out empty elements
        s = {k: v for k, v in self.__dict__.items() if v}
        o = {k: v for k, v in other.__dict__.items() if v}

        # Compare
        if s == o:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # If we define __eq__ we also need __hash__ otherwise the object
    # becomes unhashable. All this does is hash the frozenset of the
    # keys. (You can only hash immutables.)
    def __hash__(self):
        return hash(frozenset(self.__dict__.keys()))

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        rows, c = '', ''
        s = '<tr><td><strong>{k}</strong></td><td style="{stl}">{v}</td></tr>'
        for k, v in self.__dict__.items():

            if k == '_colour':
                k = 'colour'
                c = utils.text_colour_for_hex(v)
                style = 'color:{}; background-color:{}'.format(c, v)
            else:
                style = 'color:black; background-color:white'

            if k == 'component':
                try:
                    v = v._repr_html_()
                except AttributeError:
                    v = v.__repr__()

            rows += s.format(k=k, v=v, stl=style)
        html = '<table>{}</table>'.format(rows)
        return html

    def _repr_html_row_(self, keys):
        """
        Jupyter Notebook magic repr function as a row – used by
        ``Legend._repr_html_()``.
        """
        tr, th, c = '', '', ''
        r = '<td style="{stl}">{v}</td>'
        h = '<th>{k}</th>'
        for k in keys:
            v = self.__dict__.get(k)

            if k == '_colour':
                k = 'colour'
                c = utils.text_colour_for_hex(v)
                style = 'color:{}; background-color:{}'.format(c, v)
            else:
                style = 'color:black; background-color:white'

            if k == 'component':
                try:
                    v = v._repr_html_()
                except AttributeError:
                    v = v.__repr__()

            tr += r.format(v=v, stl=style)
            th += h.format(k=k)

        return th, tr

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, c):
        numbers = r'([\.0-9]+), ?([\.0-9]+), ?([\.0-9]+)'
        pattern = re.compile(r'[\(\[]?' + numbers + r'[\)\]]?')
        try:
            x = pattern.search(c)
        except:
            x = None
        if x is not None:
            try:
                x = list(map(float, x.groups()))
                if x[0] > 1 or x[1] > 1 or x[2] > 1:
                    x = [int(i) for i in x]
                colour = utils.rgb_to_hex(x)
            except KeyError:
                raise LegendError("Colour not recognized: " + c)
        elif not c:
            colour = '#eeeeee'
        elif type(c) in [list, tuple]:
            try:
                colour = utils.rgb_to_hex(c)
            except TypeError:
                raise LegendError("Colour not recognized: " + c)
        elif c[0] != '#':
            try:
                colour = utils.name_to_hex(c)
            except KeyError:
                raise LegendError("Colour not recognized: " + c)
        elif (c[0] == '#') and (len(c) == 4):
            # Three-letter hex
            colour = c[:2] + c[1] + 2*c[2] + 2*c[3]
        elif (c[0] == '#') and (len(c) == 8):
            # 8-letter hex
            colour = c[:-2]
        else:
            colour = c
        self._colour = colour

    @property
    def rgb(self):
        """
        Returns an RGB triple equivalent to the hex colour.
        """
        return utils.hex_to_rgb(self.colour)

    @property
    def keys(self):
        """
        Returns the keys of the Decor's dict.
        """
        return list(self.__dict__.keys())

    @classmethod
    def random(cls, component, match_only=None):
        """
        Returns a minimal Decor with a random colour.
        """
        c = component.__dict__.copy()
        if match_only is None:
            match_only = c.keys()

        for k in list(c.keys()):
            if k not in match_only:
                _ = c.pop(k)

        colour = random.sample([i for i in range(256)], 3)

        return cls({'colour': colour, 'component': Component(c), 'width': 1.0})

    def plot(self, fmt=None, fig=None, ax=None):
        """
        Make a simple plot of the Decor.

        Args:
            fmt (str): A Python format string for the component summaries.
            fig (Pyplot figure): A figure, optional. Use either fig or ax, not
                both.
            ax (Pyplot axis): An axis, optional. Use either fig or ax, not
                both.

        Returns:
            fig or ax or None. If you pass in an ax, you get it back. If you pass
                in a fig, you get it. If you pass nothing, the function creates a
                plot object as a side-effect.
        """

        u = 4     # aspect ratio of decor plot
        v = 0.25  # ratio of decor tile width

        r = None

        if (fig is None) and (ax is None):
            fig = plt.figure(figsize=(u, 1))
        else:
            r = fig

        if ax is None:
            ax = fig.add_axes([0.1*v, 0.1, 0.8*v, 0.8])
        else:
            r = ax

        rect1 = patches.Rectangle((0, 0),
                                  u*v, u*v,
                                  color=self.colour,
                                  lw=1,
                                  hatch=self.hatch,
                                  ec='k')
        ax.add_patch(rect1)
        ax.text(1.0+0.1*v*u, u*v*0.5,
                self.component.summary(fmt=fmt),
                fontsize=max(u, 15),
                verticalalignment='center',
                horizontalalignment='left')
        ax.set_xlim([0, u*v])
        ax.set_ylim([0, u*v])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.invert_yaxis()

        return r


class Legend(object):
    """
    A look-up table to assist in the conversion of Components to
    a plot colour.

    Args:
        list_of_Decors (list): The decors to collect into a legend. In
            general, you will want to leave legend building to the constructor
            class methods, `Legend.default()`, and
            `Legend.from_csv(text=string)`. We can add others over time, such
            as `from_xls` and so on.
    """

    def __init__(self, list_of_Decors):
        self.table = [d.__dict__ for d in list_of_Decors]
        self.__list = list_of_Decors
        self.__index = 0
        self._iter = iter(self.__list)  # Set up iterable.

    def __repr__(self):
        s = [repr(d) for d in self.__list]
        return "Legend({0})".format('\n'.join(s))

    def __str__(self):
        s = [str(d) for d in self.__list]
        return '\n'.join(s)

    def __getitem__(self, key):
        if type(key) is slice:
            i = key.indices(len(self.__list))
            result = [self.__list[n] for n in range(*i)]
            return Legend(result)
        elif type(key) is list:
            result = []
            for j in key:
                result.append(self.__list[j])
            return Legend(result)
        else:
            return self.__list[key]

    def __setitem__(self, key, value):
        self.__list[key] = value

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.__list[self.__index]
        except IndexError:
            self.__index = 0
            raise StopIteration
        self.__index += 1
        return result

    def next(self):
        """
        Retains Python 2 compatibility.
        """
        return self.__next__()

    def __len__(self):
        return len(self.__list)

    def __contains__(self, item):
        if isinstance(item, Decor):
            for d in self.__list:
                if item == d:
                    return True
        if isinstance(item, Component):
            for d in self.__list:
                if item == d.component:
                    return True
        return False

    def __add__(self, other):
        if isinstance(other, self.__class__):
            result = self.__list + other.__list
            return Legend(result)
        elif isinstance(other, Decor):
            result = self.__list + [other]
            return Legend(result)
        else:
            raise LegendError("You can only add legends or decors.")

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        all_keys = list(set(itertools.chain(*[d.keys for d in self])))
        rows = ''
        for decor in self:
            th, tr = decor._repr_html_row_(keys=all_keys)
            rows += '<tr>{}</tr>'.format(tr)
        header = '<tr>{}</tr>'.format(th)
        html = '<table>{}{}</table>'.format(header, rows)
        return html

    @classmethod
    def builtin(cls, name):
        """
        Generate a default legend.

        Args:
            name (str): The name of the legend you want. Not case sensitive.
                 'nsdoe': Nova Scotia Dept. of Energy
                 'canstrat': Canstrat
                 'nagmdm__6_2': USGS N. Am. Geol. Map Data Model 6.2
                 'nagmdm__6_1': USGS N. Am. Geol. Map Data Model 6.1
                 'nagmdm__4_3': USGS N. Am. Geol. Map Data Model 4.3
                 'sgmc': USGS State Geologic Map Compilation

            Default 'nagmdm__6_2'.

        Returns:
            Legend: The legend stored in `defaults.py`.
        """
        names = {
                 'nsdoe': LEGEND__NSDOE,
                 'canstrat': LEGEND__Canstrat,
                 'nagmdm__6_2': LEGEND__NAGMDM__6_2,
                 'nagmdm__6_1': LEGEND__NAGMDM__6_1,
                 'nagmdm__4_3': LEGEND__NAGMDM__4_3,
                 'sgmc': LEGEND__SGMC,
                 }
        return cls.from_csv(text=names[name.lower()])

    @classmethod
    def builtin_timescale(cls, name):
        """
        Generate a default timescale legend. No arguments.

        Returns:
            Legend: The timescale stored in `defaults.py`.
        """
        names = {
                 'isc': TIMESCALE__ISC,
                 'usgs_isc': TIMESCALE__USGS_ISC,
                 'dnag': TIMESCALE__DNAG,
                 }
        return cls.from_csv(text=names[name.lower()])

    # Curry.
    default = partialmethod(builtin, name="NAGMDM__6_2")
    default_timescale = partialmethod(builtin_timescale, name='ISC')

    @classmethod
    def random(cls,
               components,
               width=False,
               colour=None,
               match_only=None,
              ):
        """
        Generate a random legend for a given list of components.

        Args:
            components (list or Striplog): A list of components. If you pass
                a Striplog, it will use the primary components. If you pass a
                component on its own, you will get a random Decor.
            width (bool): Also generate widths for the components, based on the
                order in which they are encountered.
            colour (str): If you want to give the Decors all the same colour,
                provide a hex string.
            match_only (list): A list of Component properties to use.
        Returns:
            Legend or Decor: A legend (or Decor) with random colours.
        TODO:
            It might be convenient to have a partial method to generate an
            'empty' legend. Might be an easy way for someone to start with a
            template, since it'll have the components in it already.
        """
        try:  # Treating as a Striplog.
            list_of_Decors = [Decor.random(c, match_only=match_only)
                              for c
                              in [i[0] for i in components.unique if i[0]]
                              ]
        except:
            try:
                list_of_Decors = [Decor.random(c, match_only=match_only)
                                  for c in components.copy()]
            except:
                # It's a single component.
                list_of_Decors = [Decor.random(components, match_only=match_only)]

        if match_only is not None:
            # We might have duplicate components.
            comps, keeps = [], []
            for d in list_of_Decors:
                if d.component not in comps:
                    comps.append(d.component)
                    keeps.append(d)
            list_of_Decors = keeps

        if colour is not None:
            for d in list_of_Decors:
                d.colour = colour

        if width:
            for i, d in enumerate(list_of_Decors):
                d.width = i + 1

        return cls(list_of_Decors)

    @classmethod
    def from_image(cls, filename, components,
                   ignore=None,
                   col_offset=0.1,
                   row_offset=2):
        """
        A slightly easier way to make legends from images.

        Args:
            filename (str)
            components (list)
            ignore (list): Colours to ignore, e.g. "#FFFFFF" to ignore white.
            col_offset (Number): If < 1, interpreted as proportion of way
                across the image. If > 1, interpreted as pixels from left.
            row_offset (int): Number of pixels to skip at the top of each
                interval.
        """
        if ignore is None:
            ignore = []

        rgb = utils.loglike_from_image(filename, offset=col_offset)
        loglike = np.array([utils.rgb_to_hex(t) for t in rgb])

        # Get the pixels and colour values at 'tops' (i.e. changes).
        _, hexes = utils.tops_from_loglike(loglike, offset=row_offset)

        # Reduce to unique colours.
        hexes_reduced = []
        for h in hexes:
            if h not in hexes_reduced:
                if h not in ignore:
                    hexes_reduced.append(h)

        list_of_Decors = []
        for i, c in enumerate(components):
            d = Decor({'colour': hexes_reduced[i], 'component': c})
            list_of_Decors.append(d)

        return cls(list_of_Decors)

    @classmethod
    def from_striplog(cls, strip,
                      colour='colour',
                      width='width',
                      hatch='hatch',
                      fields=None,
                     ):
        """
        Creates a legend for a striplog whose components already contain.

        Args:
            components (list): list of components that need to be in the legend

        Returns:
            legend (striplog.Legend)
        """
        components = [i.primary for i in strip]
        list_of_Decors = []
        for component in components:
            f = {}
            if fields is None:
                fields = component.__dict__.keys()
            for field in fields:
                f[field] = component[field]

            d = {'component': Component(properties=f)}
            d['colour'] = component[colour]
            d['width'] = component[width]
            d['hatch'] = component[hatch]
            decor = Decor(d)
            if decor not in list_of_Decors:
                list_of_Decors.append(decor)
        return cls(list_of_Decors)

    @classmethod
    def from_csv(cls, filename=None, text=None):
        """
        Read CSV text and generate a Legend.

        Args:
            string (str): The CSV string.

        In the first row, list the properties. Precede the properties of the
        component with 'comp ' or 'component '. For example:

        colour,  width, comp lithology, comp colour
        #FFFFFF, 0, ,
        #F7E9A6, 3, Sandstone, Grey
        #FF99CC, 2, Anhydrite,
        ... etc

        Note:
            To edit a legend, the easiest thing to do is probably this:

            - `legend.to_csv()`
            - Edit the legend, call it `new_legend`.
            - `legend = Legend.from_csv(text=new_legend)`
        """
        if (filename is None) and (text is None):
            raise LegendError("You must provide a filename or CSV text.")

        if (filename is not None):
            with open(filename, 'r') as f:
                text = f.read()

        try:
            f = StringIO(text)  # Python 3
        except TypeError:
            f = StringIO(unicode(text))  # Python 2

        r = csv.DictReader(f, skipinitialspace=True)
        list_of_Decors, components = [], []
        kind = 'component'
        for row in r:
            d, component = {}, {}
            for (k, v) in row.items():
                if (k in [None, '']):
                    continue
                if (v in [None, '']):
                    if k.lower() not in ['color', 'colour']:
                        continue
                if k[:4].lower() == 'comp':
                    prop = ' '.join(k.split()[1:])
                    if v.lower() == 'true':
                        component[prop] = True
                    elif v.lower() == 'false':
                        component[prop] = False
                    else:
                        try:
                            component[prop] = float(v)
                        except ValueError:
                            component[prop] = v.lower()

                elif k[:5].lower() == 'curve':
                    prop = ' '.join(k.split()[1:])
                    component[prop] = v.lower()
                    kind = 'curve'
                else:
                    try:
                        d[k] = float(v)
                    except ValueError:
                        d[k] = v.lower()

            this_component = Component(component)
            d[kind] = this_component

            # Check for duplicates and warn.
            if this_component in components:
                with warnings.catch_warnings():
                    warnings.simplefilter("always")
                    w = "This legend contains duplicate components."
                    warnings.warn(w)
            components.append(this_component)

            # Append to the master list and continue.
            list_of_Decors.append(Decor(d))

        return cls(list_of_Decors)

    def to_csv(self):
        """
        Renders a legend as a CSV string.

        No arguments.

        Returns:
            str: The legend as a CSV.
        """
        # We can't delegate this to Decor because we need to know the superset
        # of all Decor properties. There may be lots of blanks.
        header = []
        component_header = []
        for row in self:
            for j in row.__dict__.keys():
                if j == '_colour':
                    j = 'colour'
                header.append(j)
            for k in row.component.__dict__.keys():
                component_header.append(k)
        header = set(header)
        component_header = set(component_header)
        header.remove('component')
        header_row = ''
        if 'colour' in header:
            header_row += 'colour,'
            header.remove('colour')
            has_colour = True
        for item in header:
            header_row += item + ','
        for item in component_header:
            header_row += 'component ' + item + ','

        # Now we have a header row! Phew.
        # Next we'll go back over the legend and collect everything.
        result = header_row.strip(',') + '\n'
        for row in self:
            if has_colour:
                result += row.__dict__.get('_colour', '') + ','
            for item in header:
                result += str(row.__dict__.get(item, '')) + ','
            for item in component_header:
                result += str(row.component.__dict__.get(item, '')) + ','
            result += '\n'

        return result

    @property
    def max_width(self):
        """
        The maximum width of all the Decors in the Legend. This is needed
        to scale a Legend or Striplog when plotting with widths turned on.
        """
        try:
            maximum = max([row.width for row in self.__list if row.width is not None])
            return maximum
        except:
            return 0

    def get_decor(self, c, match_only=None):
        """
        Get the decor for a component.

        Args:
           c (component): The component to look up.
           match_only (list of str): The component attributes to include in the
               comparison. Default: All of them.

        Returns:
           Decor. The matching Decor from the Legend, or None if not found.
        """
        if isinstance(c, Component):
            if c:
                if match_only:
                    # Filter the component only those attributes
                    c = Component({k: getattr(c, k, None) for k in match_only})
                for decor in self.__list:
                    try:
                        if c == decor.component:
                            return decor
                    except AttributeError:
                        continue
        else:
            for decor in self.__list:
                try:
                    if getattr(c, 'mnemonic').lower() == decor.curve.mnemonic:
                        return decor
                except AttributeError:
                    continue
        return Decor({'colour': '#eeeeee', 'component': Component()})

    def getattr(self, c, attr, default=None, match_only=None):
        """
        Get the attribute of a component.

        Args:
           c (component): The component to look up.
           attr (str): The attribute to get.
           default (str): What to return in the event of no match.
           match_only (list of str): The component attributes to include in the
               comparison. Default: All of them.

        Returns:
           obj. The specified attribute of the matching Decor in the Legend.
        """
        matching_decor = self.get_decor(c, match_only=match_only)

        try:
            return getattr(matching_decor, attr)
        except AttributeError:
            return default

    def get_colour(self, c, default='#eeeeee', match_only=None):
        """
        Get the display colour of a component. Wraps `getattr()`.

        Development note:
            Cannot define this as a `partial()` because I want
            to maintain the order of arguments in `getattr()`.

        Args:
           c (component): The component to look up.
           default (str): The colour to return in the event of no match.
           match_only (list of str): The component attributes to include in the
               comparison. Default: All of them.

        Returns:
           str. The hex string of the matching Decor in the Legend.
        """
        return self.getattr(c=c,
                            attr='colour',
                            default=default,
                            match_only=match_only)

    def get_width(self, c, default=0, match_only=None):
        """
        Get the display width of a component. Wraps `getattr()`.

        Development note: Cannot define this as a `partial()` because I want
        to maintain the order of arguments in `getattr()`.

        Args:
            c (component): The component to look up.
            default (float): The width to return in the event of no match.
            match_only (list of str): The component attributes to include in the
                comparison. Default: All of them.

        Returns:
            float. The width of the matching Decor in the Legend.
        """
        return self.getattr(c=c,
                            attr='width',
                            default=default,
                            match_only=match_only)

    def get_component(self, colour, tolerance=0, default=None):
        """
        Get the component corresponding to a display colour. This is for
        generating a Striplog object from a colour image of a striplog.

        Args:
           colour (str): The hex colour string to look up.
           tolerance (float): The colourspace distance within which to match.
           default (component or None): The component to return in the event
           of no match.

        Returns:
           component. The component best matching the provided colour.
        """
        if not (0 <= tolerance <= np.sqrt(195075)):
            raise LegendError('Tolerance must be between 0 and 441.67')

        for decor in self.__list:
            if colour.lower() == decor.colour:
                return decor.component

        # If we're here, we didn't find one yet.
        r1, g1, b1 = utils.hex_to_rgb(colour)

        # Start with a best match of black.
        best_match = '#000000'
        best_match_dist = np.sqrt(r1**2. + g1**2. + b1**2.)

        # Now compare to each colour in the legend.
        for decor in self.__list:
            r2, g2, b2 = decor.rgb
            distance = np.sqrt((r2-r1)**2. + (g2-g1)**2. + (b2-b1)**2.)
            if distance < best_match_dist:
                best_match = decor.component
                best_match_dist = distance
                best_match_colour = decor.colour

        if best_match_dist <= tolerance:
            return best_match
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                w = "No match found for {0} ".format(colour.lower())
                w += "with tolerance of {0}. Best match is ".format(tolerance)
                w += "{0}, {1}".format(best_match.summary(), best_match_colour)
                w += ", d={0}".format(best_match_dist)
                warnings.warn(w)

            return default

    def plot(self, fmt=None, ax=None):
        """
        Make a simple plot of the legend.

        Calls Decor.plot() on all of its members.

        TODO: Build a more attractive plot.
        """
        if ax is None:
            fig, ax = plt.subplots()
            return_ax = False
        else:
            return_ax = True

        height = width = (0.9 / len(self))
        h_incr = 1 / len(self)
        left_pos = 0.1
        bot_pos = 0.0
        for decor in self:
            cax = utils.add_subplot_axes(ax, [left_pos, bot_pos, width, height])
            cax = decor.plot(ax=cax)
            bot_pos += h_incr
        ax.axis('off')

        if return_ax:
            return ax
        else:
            plt.show()
