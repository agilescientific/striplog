"""
Helper functions for the striplog package.

"""
from string import Formatter
from functools import partial
import re
import shlex

import requests
import numpy as np
import matplotlib.pyplot as plt

from . import defaults

try:
    from IPython.display import HTML
    ipy = True
except ImportError:
    ipy = False
    pass


def binary_dilation(arr, p):
    """
    1D binary morphology: dilation.

    TODO
        None of these operators work with 'greyscale' (i.e. non-binary) data.
        And none of them work with non-boxcar structure elements. They could be
        easily re-written to be much more general. (They are only here to avoid
        dependency on SciPy, which probably is not that big a deal, so could
        just revert to `scipy.morphology`.)

    Args:
        arr: A binary array (e.g. [1,0,0,1,0]).
        p: Structuring element length.

    Returns:
        ndarray
    """
    structure = np.ones(int(p))
    L = len(structure)
    if L == 1:
        return arr
    out = (np.convolve(arr, structure, mode='full') > 0).astype(int)
    start = L // 2

    # Why is this so complicated??
    if L % 2:  # if L is odd...
        end = - (L // 2) if L > 3 else -1
    else:
        end = 1 - (L // 2) if L > 3 else None

    return out[start:end]


def binary_erosion(arr, p):
    """
    1D binary morphology: erosion.

    Args:
        arr: A binary array (e.g. [1,0,0,1,0]).
        p: Structuring element length.

    Returns:
        ndarray
    """
    structure = np.ones(int(p))
    L = len(structure)
    return (np.convolve(arr, structure, mode='same') >= L).astype(int)


def binary_opening(arr, p):
    """
    1D binary morphology: opening.

    Args:
        arr: A binary array (e.g. [1,0,0,1,0]).
        p: Structuring element length.

    Returns:
        ndarray
    """
    return binary_dilation(binary_erosion(arr, p), p)


def binary_closing(arr, p):
    """
    1D binary morphology: closing.

    Args:
        arr: A binary array (e.g. [1,0,0,1,0]).
        p: Structuring element length.

    Returns:
        ndarray
    """
    return binary_erosion(binary_dilation(arr, p), p)


def observations(seq_of_seqs, states, step=1, include_self=False):
    """
    Compute observation matrix.
    """
    O = np.zeros(tuple(states.size for _ in range(step+1)))
    for seq in seq_of_seqs:
        seq = np.array(seq)
        _, integer_seq = np.where(seq.reshape(-1, 1) == states)
        for idx in zip(*[integer_seq[n:] for n in range(step+1)]):
            if (not include_self) and (0 in np.diff(idx)):
                continue
            O[idx] += 1
    return O


def hollow_matrix(M):
    """
    Return hollow matrix (zeros on diagonal).

    Args
        M (ndarray): a 'square' ndarray.

    Returns
        ndarray. The same array with zeros on the diagonal.
    """
    s = M.shape[0]
    idx = np.unravel_index(np.arange(0, s**2, s + 1), M.shape)
    M[idx] = 0
    return M


def inspect_petrel(filename):
    data = read_petrel(filename)
    data = {k: ', '.join(list(map(str, set(v)))) for k, v in data.items()}
    if ipy:
        return HTML(dict_repr_html(data))
    else:
        return data


def read_petrel(filename, function=None, remap=None):
        """
        Read a Petrel well tops ASCII export file.

        Args:
            filename (str): The name of the ASCII file.
            function (function or dict): A function to apply to every field,
                or a mapping of field name to function. The result of the
                function will be used as the value for that field.
            remap (dict): A mapping of field name to new field name. The
                field name will be replaced.

        Returns:
            dict: A mapping of field names to lists of data. You can give this
                straight to `pandas`.
        """
        with open(filename, 'r') as f:
            text = f.read()

        # Gather fieldnames from header.
        s = re.search(r'BEGIN HEADER(.+?)END HEADER', text, flags=re.DOTALL)
        fieldnames = list(filter(None, s.groups()[0].split('\n')))

        function = function or {}

        if remap is not None:
            fieldnames = [remap.get(f, f) for f in fieldnames]

        def fixer(s):
            # Make floats
            try:
                s = float(s)
            except ValueError:
                pass
            # Correct strings
            try:
                s = s.strip(""" "'""")
            except:
                pass
            if s == 'TRUE':
                s = True
            if s == 'FALSE':
                s = False
            return s

        # Gather data.
        end = 'END HEADER'
        rows = filter(None, text[text.find(end) + len(end):].split('\n'))
        data = [list(map(fixer, shlex.split(row))) for row in rows]

        result = {}
        for i, f in enumerate(fieldnames):
            if not callable(function):
                # Treat as mapping of fieldname to function.
                function = function.get(f, identity)
            result[f] = [function(d[i]) for d in data]

        return result


class CustomFormatter(Formatter):
    """
    Extends the Python string formatter to some new functions.
    """
    def __init__(self):
        super(CustomFormatter, self).__init__()

    def get_field(self, field_name, args, kwargs):
        """
        Return an underscore if the attribute is absent.
        Not all components have the same attributes.
        """
        try:
            s = super(CustomFormatter, self)
            return s.get_field(field_name, args, kwargs)
        except KeyError:    # Key is missing
            return ("_", field_name)
        except IndexError:  # Value is missing
            return ("_", field_name)

    def convert_field(self, value, conversion):
        """
        Define some extra field conversion functions.
        """
        try:  # If the normal behaviour works, do it.
            s = super(CustomFormatter, self)
            return s.convert_field(value, conversion)
        except ValueError:
            funcs = {'s': str,    # Default.
                     'r': repr,   # Default.
                     'a': ascii,  # Default.
                     'u': str.upper,
                     'l': str.lower,
                     'c': str.capitalize,
                     't': str.title,
                     'm': np.mean,
                     'µ': np.mean,
                     'v': np.var,
                     'd': np.std,
                     '+': np.sum,
                     '∑': np.sum,
                     'x': np.product,
                     }
            return funcs.get(conversion)(value)


def dict_repr_html(dictionary):
    """
    Jupyter Notebook magic repr function.
    """
    rows = ''
    s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
    for k, v in dictionary.items():
        rows += s.format(k=k, v=v)
    html = '<table>{}</table>'.format(rows)
    return html


class partialmethod(partial):
    """
    Extends partial to work on class methods.
    """
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func,
                       instance,
                       *(self.args or ()),
                       **(self.keywords or {})
                       )


def null(x):
    """
    Null function. Used for default in functions that can apply a user-
    supplied function to data before returning.
    """
    return x

identity = null


def null_default(x):
    """
    Null function. Used for default in functions that can apply a user-
    supplied function to data before returning.
    """
    def null(y):
        return x

    return null


def skip(x):
    """
    Always returns None.
    """
    return


def are_close(x, y):
    return abs(x - y) < 0.00001


def hex_to_name(hexx):
    """
    Convert hex to a color name, using matplotlib's colour names.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        str: The name of the colour, or None if not found.
    """
    for n, h in defaults.COLOURS.items():
        if (len(n) > 1) and (h == hexx.upper()):
            return n.lower()
    return None


def name_to_hex(name):
    """
    Convert a color name to hex, using matplotlib's colour names.

    Args:
        name (str): The name of a colour, e.g. 'red'.

    Returns:
        str: The hex code for the colour.
    """
    return defaults.COLOURS[name.lower()].lower()


def rgb_to_hex(rgb):
    """
    Utility function to convert (r,g,b) triples to hex.
    http://ageo.co/1CFxXpO
    Args:
      rgb (tuple): A sequence of RGB values in the
        range 0-255 or 0-1.
    Returns:
      str: The hex code for the colour.
    """
    r, g, b = rgb[:3]
    if (r < 0) or (g < 0) or (b < 0):
            raise Exception("RGB values must all be 0-255 or 0-1")
    if (r > 255) or (g > 255) or (b > 255):
            raise Exception("RGB values must all be 0-255 or 0-1")
    if (0 < r < 1) or (0 < g < 1) or (0 < b < 1):
        if (r > 1) or (g > 1) or (b > 1):
            raise Exception("RGB values must all be 0-255 or 0-1")
    if (0 <= r <= 1) and (0 <= g <= 1) and (0 <= b <= 1):
        rgb = tuple([int(round(val * 255)) for val in [r, g, b]])
    else:
        rgb = (int(r), int(g), int(b))
    result = '#%02x%02x%02x' % rgb
    return result.lower()


def hex_to_rgb(hexx):
    """
    Utility function to convert hex to (r,g,b) triples.
    http://ageo.co/1CFxXpO

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        tuple: The equivalent RGB triple, in the range 0 to 255.
    """
    h = hexx.strip('#')
    l = len(h)

    return tuple(int(h[i:i+l//3], 16) for i in range(0, l, l//3))


def hex_is_dark(hexx, percent=50):
    """
    Function to decide if a hex colour is dark.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        bool: The colour's brightness is less than the given percent.
    """
    r, g, b = hex_to_rgb(hexx)
    luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 2.55  # per ITU-R BT.709

    return (luma < percent)


def rgb_is_dark(rgb, percent=50):
    """
    Helpful wrapper for hex_is_dark.
    """
    return hex_is_dark(rgb_to_hex(rgb))


def text_colour_for_hex(hexx, percent=50, dark='#000000', light='#ffffff'):
    """
    Function to decide what colour to use for a given hex colour.

    Args:
        hexx (str): A hexadecimal colour, starting with '#'.

    Returns:
        bool: The colour's brightness is less than the given percent.
    """
    return light if hex_is_dark(hexx, percent=percent) else dark


def loglike_from_image(filename, offset):
    """
    Get a log-like stream of RGB values from an image.

    Args:
        filename (str): The filename of a PNG image.
        offset (Number): If < 1, interpreted as proportion of way across
            the image. If > 1, interpreted as pixels from left.

    Returns:
        ndarray: A 2d array (a column of RGB triples) at the specified
        offset.

    TODO:
        Generalize this to extract 'logs' from images in other ways, such
        as giving the mean of a range of pixel columns, or an array of
        columns. See also a similar routine in pythonanywhere/freqbot.
    """
    im = plt.imread(filename)
    if offset < 1:
        col = int(im.shape[1] * offset)
    else:
        col = offset
    return im[:, col, :3]


def tops_from_loglike(a, offset=0, null=None):
    """
    Take a log-like stream of numbers or strings, and return two arrays:
    one of the tops (changes), and one of the values from the stream.

    Args:
        loglike (array-like): The input stream of loglike data.
        offset (int): Offset (down) from top at which to get lithology,
            to be sure of getting 'clean' pixels.

    Returns:
        ndarray: Two arrays, tops and values.
    """
    a = np.copy(a)

    try:
        contains_nans = np.isnan(a).any()
    except:
        contains_nans = False

    if contains_nans:
        # Find a null value that's not in the log, and apply it if possible.
        _null = null or -1
        while _null in a:
            _null -= 1

        try:
            a[np.isnan(a)] = _null
            transformed = True
        except:
            transformed = False

    edges = a[1:] == a[:-1]
    edges = np.append(True, edges)

    tops = np.where(~edges)[0]
    tops = np.append(0, tops)

    values = a[tops + offset]

    if contains_nans and transformed:
        values[values == _null] = np.nan

    return tops, values


def list_and_add(a, b):
    """
    Coerce to lists and concatenate.

    Args:
        a: A thing.
        b: A thing.

    Returns:
        List. All the things.
    """
    if not isinstance(b, list):
        b = [b]
    if not isinstance(a, list):
        a = [a]
    return a + b


def flatten_list(l):
    """
    Unpacks lists in a list:

        [1, 2, [3, 4], [5, [6, 7]]]

    becomes

        [1, 2, 3, 4, 5, 6, 7]

    http://stackoverflow.com/a/12472564/3381305
    """
    if (l == []) or (l is None):
        return l
    if isinstance(l[0], list) or isinstance(l[0], tuple):
        return flatten_list(l[0]) + flatten_list(l[1:])
    return l[:1] + flatten_list(l[1:])


def axis_transform(ax, x, y, xlim=None, ylim=None, inverse=False):
    """
    http://stackoverflow.com/questions/29107800

    inverse = False : Axis => Data
            = True  : Data => Axis
    """
    xlim = xlim or ax.get_xlim()
    ylim = ylim or ax.get_ylim()

    xdelta = xlim[1] - xlim[0]
    ydelta = ylim[1] - ylim[0]

    if not inverse:
        xout = xlim[0] + x * xdelta
        yout = ylim[0] + y * ydelta
    else:
        xdelta2 = x - xlim[0]
        ydelta2 = y - ylim[0]
        xout = xdelta2 / xdelta
        yout = ydelta2 / ydelta

    return xout, yout


def add_subplot_axes(ax, rect, axisbg='w'):
    """
    Facilitates the addition of a small subplot within another plot.
    From: http://stackoverflow.com/questions/17458580/
    embedding-small-plots-inside-subplots-in-matplotlib
    License: CC-BY-SA
    Args:
        ax (axis): A matplotlib axis.
        rect (list): A rect specifying [left pos, bot pos, width, height]
    Returns:
        axis: The sub-axis in the specified position.
    """
    def axis_to_fig(axis):
        fig = axis.figure

        def transform(coord):
            a = axis.transAxes.transform(coord)
            return fig.transFigure.inverted().transform(a)

        return transform

    fig = plt.gcf()
    left, bottom, width, height = rect
    trans = axis_to_fig(ax)
    x1, y1 = trans((left, bottom))
    x2, y2 = trans((left + width, bottom + height))
    subax = fig.add_axes([x1, y1, x2 - x1, y2 - y1])
    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()
    x_labelsize *= rect[2] ** 0.5
    y_labelsize *= rect[3] ** 0.5
    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax


def geology_from_macrostrat(lng, lat, buffer_size=0.2):
    """
    Request data from MacroStrat within `buffer_size` of a given lng, lat pair.
    We can do this by creating a WKT polygon, which is simply a square with
        each side a `buffer_size` distance from the given lng, lat. 

    Args:
        lng (float): longitude in decimal degrees.
        lat (float): latitude in decimal degrees.
        buffer_size (float): distance in decimal degrees to add to lng
                            and lat to request geology in.
    
    Returns:
        polygon_request (requests.models.Response) 
    """
    area = f'POLYGON(( {lng-buffer_size} {lat+buffer_size}, \
        {lng+buffer_size} {lat+buffer_size}, \
            {lng+buffer_size} {lat-buffer_size}, \
                {lng-buffer_size} {lat-buffer_size}, \
                    {lng-buffer_size} {lat+buffer_size}))'

    url = 'https://macrostrat.org/api/carto/small'
    params = {'shape': area, 'format': 'geojson_bare'}
    r = requests.get(url, params=params)

    return r.json()['features']

def get_liths_from_macrostrat(s):
    """
    Parse a Macrostrat 'lith' string into lithologies.
    """
    if 'Major' in s:
        nested, = re.findall(r'Major:{(.+?)}, Minor{(.+?)}', s)
        split = [i.split(',') for i in nested]
        return flatten_list(split)
    else:
        return [s]
