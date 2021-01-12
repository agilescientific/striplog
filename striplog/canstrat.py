"""
Functions for importing Canstrat ASCII files.

:copyright: 2016 Agile Geoscience
:license: Apache 2.0
"""
import datetime as dt

from .utils import null, skip, are_close

from .canstrat_codes import rtc
from .canstrat_codes import fwork
from .canstrat_codes import grains
from .canstrat_codes import colour
from .canstrat_codes import cmod
from .canstrat_codes import porgrade
from .canstrat_codes import stain
from .canstrat_codes import oil


def _colour_read(x):
    try:
        c1 = colour[x[1]]
    except:
        c1 = ''
    try:
        c0 = colour[x[0]]
    except:
        c0 = ''
    try:
        m = cmod[x[2]]
    except:
        m = ''
    return ' '.join([m, c0, c1]).strip().replace('  ', ' ')


def _get_date(date_string):
    try:
        date = dt.datetime.strptime(date_string, "%y-%m-%d")
    except:
        date = dt.datetime.strptime("00-01-01", "%y-%m-%d")
    if dt.datetime.today() < date:
        date -= dt.timedelta(days=100*365.25)
    return dt.datetime.date(date)


def _put_date(date):
    return dt.datetime.strftime(date, '%y-%m-%d')


columns_ = {
    # name: start, run, read, write
    'log':  [0,    6, null, null],
    'card': [6,    1, lambda x: int(x) if x else None, null],
    'skip': [7,    1, lambda x: True if x == 'X' else False, lambda x: 'X' if x else ' '],
    'core': [8,    1, lambda x: True if x == 'C' else False, lambda x: 'C' if x else ' '],
    'data': [9,    73,  null, null],
}

# Columns for card type 1
columns_1 = {
    'location': [8, 18, lambda x: x.strip(), null],
    'loctype': [18, 1, lambda x: {' ': 'NTS', '-': 'LL'}.get(x, 'LSD'), null],
    'units': [26, 1, null, null],
    'name': [27, 40, lambda x: x.strip(), null],
    'kb': [67, 2, null, null],
    'elev': [69, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
    'metric': [74, 1, lambda x: x if x == 'M' else 'I', lambda x: x if x == 'M' else ' '],
    'td': [75, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
}

# Columns for card type 1
columns_2 = {
    'spud': [8, 8, _get_date, _put_date],
    'comp': [18, 8, _get_date, _put_date],
    'status': [27, 13, lambda x: x.strip(), null],
    'uwi': [50, 16, null, null],
    'start': [69, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
    'stop': [75, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
}

# Columns for card type 1
columns_8 = {
    'formation': [14, 3, lambda x: x.strip(), null],
    'top': [24, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
}


columns_7 = {
    'skip': [7, 1, lambda x: True if x == 'X' else False, lambda x: 'X' if x else ' '],
    'core': [8, 1, lambda x: True if x == 'C' else False, lambda x: 'C' if x else ' '],
    'top': [9, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
    'base': [14, 5, lambda x: float(x)/10, lambda x: '{:5.0f}'.format(10*x)],
    'lithology': [19, 8, lambda x: x.replace(' ', '.'), skip],
    'rtc_id': [19, 1, null, null],
    'rtc': [19, 1, lambda x: rtc[x], skip],
    'rtc_idperc': [20, 1, lambda x: int(x)*10 if int(x) > 0 else 100, lambda x: '{:1.0f}'.format(x/10) if x < 100 else '0'],
    'grains_mm': [21, 1, lambda x: grains[x], lambda x: [k for k, v in grains.items() if are_close(v, x)][0]],
    'framew_per': [22, 2, lambda x: fwork[x], lambda x: {v: k for k, v in fwork.items()}[x]],
    'colour': [24, 3, lambda x: x.replace(' ', '.'), lambda x: x.replace('.', ' ')],
    'colour_name': [24, 3, _colour_read, skip],
    'accessories': [27, 18, lambda x: x.strip(), lambda x: '{:18s}'.format(x)],
    'porgrade': [45, 1, lambda x: porgrade[x] if x.replace(' ', '') else 0, skip],
    'stain': [48, 1,  lambda x: stain.get(x, ' '), lambda x: {v: k for k, v in stain.items()}.get(x, '')],
    'oil': [48, 1,  lambda x: oil.get(x, 0), skip],
}

columns = {
    0: columns_,   # Row header, applies to every row
    1: columns_1,  # Location, depth measure, well name, elev, td
    2: columns_2,  # Spud and completion data, status, UWI, Interval coded
    7: columns_7,  # Lithology
    8: columns_8,  # Formation tops
}


def _get_field(text, coldict, key):
    data = coldict[key]
    strt = data['start']
    stop = strt + data['len']
    transform = data['read']
    fragment = text[strt:stop]
    if fragment:
        return transform(fragment)
    else:
        return


def _process_row(text, columns):
    """
    Processes a single row from the file.
    """
    if not text:
        return

    # Construct the column dictionary that maps each field to
    # its start, its length, and its read and write functions.
    coldict = {k: {'start': s,
                   'len': l,
                   'read': r,
                   'write': w} for k, (s, l, r, w) in columns.items()}

    # Now collect the item
    item = {}
    for field in coldict:
        value = _get_field(text, coldict, field)
        if value is not None:
            item[field] = value

    return item


def parse_canstrat(text):
    """
    Read all the rows and return a dict of the results.
    """
    result = {}
    for row in text.split('\n'):
        if not row:
            continue

        if len(row) < 8:  # Not a real record.
            continue

        # Read the metadata for this row/
        row_header = _process_row(row, columns_) or {'card': None}
        card = row_header['card']

        # Now we know the card type for this row, we can process it.
        if card is not None:
            item = _process_row(row, columns[card])

        this_list = result.get(card, [])
        this_list.append(item)
        result[card] = this_list

    # Flatten if possible.
    for c, d in result.items():
        if len(d) == 1:
            result[c] = d[0]

    return result
