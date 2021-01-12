"""
Defines components for holding properties of rocks or samples or whatevers.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import json

from .lexicon import Lexicon
from .utils import CustomFormatter


class ComponentError(Exception):
    """
    Generic error class.
    """
    pass


class Component(object):
    """
    Initialize with a dictionary of properties. You can use any
    properties you want e.g.:

        - lithology: a simple one-word rock type
        - colour, e.g. 'grey'
        - grainsize or range, e.g. 'vf-f'
        - modifier, e.g. 'rippled'
        - quantity, e.g. '35%', or 'stringers'
        - description, e.g. from cuttings
    """

    def __init__(self, properties=None):
        if properties is not None:
            for k, v in properties.items():
                if v is True or v is False:
                    # Cope with a boolean...
                    setattr(self, k, v)
                else:
                    try:  # To treat as number...
                        setattr(self, k, float(v))
                    except ValueError:  # Just add it.
                        setattr(self, k, v)
                    except TypeError:  # It's probably None.
                        continue

    def __str__(self):
        return self.__dict__.__str__()

    def __repr__(self):
        s = str(self)
        return "Component({0})".format(s)

    def __len__(self):
        return len(self.__dict__)

    def __copy__(self):
        return Component(self.__dict__.copy())

    copy = __copy__

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        return

    def __delitem__(self, key):
        del self.__dict__[key]
        return

    def __bool__(self):
        if not self.__dict__.keys():
            return False
        else:
            return True

    # For Python 2
    __nonzero__ = __bool__

    def __eq__(self, other):
        """
        Equals

        Definitely a debate to be had about what constitutes equality. Here,
        we are ignoring numerical fields in the components, but not Boolean
        ones.
        """
        if not isinstance(other, self.__class__):
            return False

        ds = self.__dict__.items()
        do = other.__dict__.items()

        try:
            strobj = basestring  # Fails in Python 3
        except:
            strobj = str

        # Weed out empty elements and case-desensitize.
        try:
            s = {k.lower(): v.lower() for k, v in ds if v}
            o = {k.lower(): v.lower() for k, v in do if v}
        except (AttributeError, ValueError):  # Dealing with numbers.
            s = {k.lower(): v for k, v in ds if isinstance(v, strobj) or isinstance(v, bool)}
            o = {k.lower(): v for k, v in do if isinstance(v, strobj) or isinstance(v, bool)}

        # Compare.
        if s == o:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        If we define __eq__ we also need __hash__ otherwise the object
        becomes unhashable. All this does is hash the frozenset of the
        keys. (You can only hash immutables.)
        """
        return hash(frozenset(self.__dict__.keys()))

    def keys(self):
        """
        Needed for double-star behaviour, along with __getitem__().
        """
        return self.__dict__.keys()

    def _repr_html_(self):
        """
        Jupyter Notebook magic repr function.
        """
        rows = ''
        s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
        for k, v in self.__dict__.items():
            rows += s.format(k=k, v=v)
        html = '<table>{}</table>'.format(rows)
        return html

    def json(self):
        """
        Returns a JSON dump of the dictionary representation of the instance.
        """
        return json.dumps(self.__dict__)

    @classmethod
    def from_text(cls, text, lexicon=None, required=None, first_only=True):
        """
        Generate a Component from a text string, using a Lexicon.

        Args:
            text (str): The text string to parse.
            lexicon (Lexicon): The dictionary to use for the
                categories and lexemes.
            required (str): An attribute that we must have. If a required
                attribute is missing from the component, then None is returned.
            first_only (bool): Whether to only take the first
                match of a lexeme against the text string.

        Returns:
            Component: A Component object, or None if there was no
                must-have field.
        """
        if lexicon is None:
            lexicon = Lexicon.default()
        component = lexicon.get_component(text, first_only=first_only)
        if required and (required not in component):
            return None
        else:
            return cls(component)

    @classmethod
    def from_macrostrat(cls, feature, columns=None):
        """
        Make a Component from a Macrostrat feature dictionary.
        """
        props = feature['properties']
        if columns is None:
            columns = []
        for column in columns:
            if props.get(column) is None:
                if column == 'color': # skip if no colour
                    continue
                props[column] = '' # Need a value to match on.
                continue
            else:
                props[column] = props[column].replace(',', ';').lower()
        props['source'] = 'Macrostrat.org (CC-BY)'
        return cls(props)

    def summary(self, fmt=None, initial=True, default=''):
        """
        Given a format string, return a summary description of a component.

        Args:
            component (dict): A component dictionary.
            fmt (str): Describes the format with a string. If no format is
                given, you will just get a list of attributes. If you give the
                empty string (''), you'll get `default` back. By default this
                gives you the empty string, effectively suppressing the
                summary.
            initial (bool): Whether to capitialize the first letter. Default is
                True.
            default (str): What to give if there's no component defined.

        Returns:
            str: A summary string.

        Example:

            r = Component({'colour': 'Red',
                           'grainsize': 'VF-F',
                           'lithology': 'Sandstone'})

            r.summary()  -->  'Red, vf-f, sandstone'
        """
        if default and not self.__dict__:
            return default

        if fmt == '':
            return default

        keys = [k for k, v in self.__dict__.items() if v is not '']

        f = fmt or '{' + '}, {'.join(keys) + '}'

        try:
            summary = CustomFormatter().format(f, **self.__dict__)
        except KeyError as e:
            raise ComponentError("Error building summary, "+str(e))

        if summary and initial and not fmt:
            summary = summary[0].upper() + summary[1:]

        return summary
