"""
A vocabulary for parsing lithologic or stratigraphic decriptions.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
from io import open
import json
import warnings
import re
from itertools import islice
from copy import deepcopy

from . import defaults

SPECIAL = ['synonyms', 'splitters', 'parts_of_speech', 'abbreviations']


class LexiconError(Exception):
    """
    Generic error class.
    """
    pass


class Lexicon(object):
    """
    A Lexicon is a dictionary of 'types' and regex patterns.

    Most commonly you will just load the default one.

    Args:
        params (dict): The dictionary to use. For an example, refer to the
            default lexicon in ``defaults.py``.
    """

    def __init__(self, params):
        for k, v in params.items():
            k = re.sub(' ', '_', k)
            setattr(self, k, v)

        # Make sure the special attributes are set.
        # We probably don't really need to do this.
        for attr in SPECIAL:
            if not getattr(self, attr, None):
                setattr(self, attr, None)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        keys = self.__dict__.keys()
        counts = [len(v) for k, v in self.__dict__.items() if v]
        s = "Lexicon("
        for i in zip(keys, counts):
            s += "'{0}': {1} items, ".format(*i)
        s += ")"
        return s

    @classmethod
    def default(cls):
        """
        Makes the default lexicon, as provided in ``defaults.py``.

        Returns:
            Lexicon: The default lexicon.
        """
        return cls(deepcopy(defaults.LEXICON))

    @classmethod
    def from_json_file(cls, filename):
        """
        Load a lexicon from a JSON file.

        Args:
            filename (str): The path to a JSON dump.
        """
        with open(filename, 'r') as fp:
            return cls(json.load(fp))

    def find_word_groups(self, text, category, proximity=2):
        """
        Given a string and a category, finds and combines words into
        groups based on their proximity.

        Args:
            text (str): Some text.
            tokens (list): A list of regex strings.

        Returns:
            list. The combined strings it found.

        Example:
            COLOURS = [r"red(?:dish)?", r"grey(?:ish)?", r"green(?:ish)?"]
            s = 'GREYISH-GREEN limestone with RED or GREY sandstone.'
            find_word_groups(s, COLOURS) --> ['greyish green', 'red', 'grey']
        """
        f = re.IGNORECASE
        words = getattr(self, category)
        regex = re.compile(r'(\b' + r'\b|\b'.join(words) + r'\b)', flags=f)
        candidates = regex.finditer(text)

        starts, ends = [], []
        groups = []

        for item in candidates:
            starts.append(item.span()[0])
            ends.append(item.span()[1])
            groups.append(item.group().lower())

        new_starts = []  # As a check only.
        new_groups = []  # This is what I want.

        skip = False
        for i, g in enumerate(groups):
            if skip:
                skip = False
                continue
            if (i < len(groups)-1) and (starts[i+1]-ends[i] <= proximity):
                if g[-1] == '-':
                    sep = ''  # Don't insert spaces after hyphens.
                else:
                    sep = ' '
                new_groups.append(g + sep + groups[i+1])
                new_starts.append(starts[i])
                skip = True
            else:
                if g not in new_groups:
                    new_groups.append(g)
                    new_starts.append(starts[i])
                skip = False

        return new_groups

    def find_synonym(self, word):
        """
        Given a string and a dict of synonyms, returns the 'preferred'
        word. Case insensitive.

        Args:
            word (str): A word.

        Returns:
            str: The preferred word, or the input word if not found.

        Example:
            >>> syn = {'snake': ['python', 'adder']}
            >>> find_synonym('adder', syn)
            'snake'
            >>> find_synonym('rattler', syn)
            'rattler'

        TODO:
            Make it handle case, returning the same case it received.
        """
        if word and self.synonyms:
            # Make the reverse look-up table.
            reverse_lookup = {}
            for k, v in self.synonyms.items():
                for i in v:
                    reverse_lookup[i.lower()] = k.lower()

            # Now check words against this table.
            if word.lower() in reverse_lookup:
                return reverse_lookup[word.lower()]

        return word

    def expand_abbreviations(self, text):
        """
        Parse a piece of text and replace any abbreviations with their full
        word equivalents. Uses the lexicon.abbreviations dictionary to find
        abbreviations.

        Args:
            text (str): The text to parse.

        Returns:
            str: The text with abbreviations replaced.
        """
        if not self.abbreviations:
            raise LexiconError("No abbreviations in lexicon.")

        def chunks(data, SIZE=25):
            """
            Regex only supports 100 groups for munging callbacks. So we have to
            chunk the abbreviation dicitonary.
            """
            it = iter(data)
            for i in range(0, len(data), SIZE):
                yield {k: data[k] for k in islice(it, SIZE)}

        def cb(g):
            """Regex callback"""
            return self.abbreviations.get(g.group(0)) or g.group(0)

        # Special cases.

        # TODO: We should handle these with a special set of
        # replacements that are made before the others.
        text = re.sub(r'w/', r'wi', text)

        # Main loop.
        for subdict in chunks(self.abbreviations):
            regex = r'(\b' + r'\b)|(\b'.join(subdict.keys()) + r'\b)'
            text = re.sub(regex, cb, text)

        return text

    def get_component(self, text, required=False, first_only=True):
        """
        Takes a piece of text representing a lithologic description for one
        component, e.g. "Red vf-f sandstone" and turns it into a dictionary
        of attributes.

        TODO:
            Generalize this so that we can use any types of word, as specified
            in the lexicon.
        """
        component = {}

        for i, (category, words) in enumerate(self.__dict__.items()):

            # There is probably a more elegant way to do this.
            if category in SPECIAL:
                # There are special entries in the lexicon.
                continue

            groups = self.find_word_groups(text, category)

            if groups and first_only:
                groups = groups[:1]
            elif groups:
                # groups = groups
                pass
            else:
                groups = [None]
                if required:
                    with warnings.catch_warnings():
                        warnings.simplefilter("always")
                        w = "No lithology in lexicon matching '{0}'"
                        warnings.warn(w.format(text))

            filtered = [self.find_synonym(i) for i in groups]
            if first_only:
                component[category] = filtered[0]
            else:
                component[category] = filtered

        return component

    def split_description(self, text):
        """
        Split a description into parts, each of which can be turned into
        a single component.
        """
        # Protect some special sequences.
        t = re.sub(r'(\d) ?in\. ', r'\1 inch ', text)  # Protect.
        t = re.sub(r'(\d) ?ft\. ', r'\1 feet ', t)  # Protect.

        # Transform all part delimiters to first splitter.
        words = getattr(self, 'splitters')
        try:
            splitter = words[0].strip()
        except:
            splitter = 'with'
        t = re.sub(r'\,?\;?\.? ?((under)?(less than)? \d+%) (?=\w)', r' '+splitter+' \1 ', t)

        # Split.
        f = re.IGNORECASE
        pattern = re.compile(r'(?:' + r'|'.join(words) + r')', flags=f)
        parts = filter(None, pattern.split(t))

        return [i.strip() for i in parts]

    @property
    def categories(self):
        """
        Lists the categories in the lexicon, except the
        optional categories.

        Returns:
            list: A list of strings of category names.
        """
        keys = [k for k in self.__dict__.keys() if k not in SPECIAL]
        return keys

    def parse_description(self, text):
        """
        Parse a single description into component-like dictionaries.
        """
        components = []
        for descr in self.split_description(text):
            expanded = self.expand_abbreviations(descr)
            component = self.get_component(expanded)
            components.append(component)
        return components
