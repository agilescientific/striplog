#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines some default values for parsing cuttings descriptions.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""
import xlrd

def get_abbreviations_from_xls(fname):
    """
    Given a filename to an Excel spreadsheet containing abbreviations,
    return a dictionary with abbrev:definition key:value pairs.

    Args:
        fname (str): The path of an Excel .xls file.

    Returns:
        dict: A mapping of abbreviation to definition.
    """
    book = xlrd.open_workbook(fname)
    abbreviations = {}
    for s in range(book.nsheets):
        sh = book.sheet_by_index(s)
        abbrs = [c.value.encode('utf-8').strip() for c in sh.col(0)]
        defns = [c.value.encode('utf-8').strip() for c in sh.col(1)]
        for i, a in enumerate(abbrs):
            abbreviations[a] = defns[i]

    return abbreviations

ABBREVIATIONS = get_abbreviations_from_xls('../data/Abbreviations.xlsx')

LEGEND = """colour, width, rock lithology, rock colour, rock grainsize
#FFFFFF, 0, , , 
#F7E9A6, 3, Sandstone, Grey, VF-F
#FF99CC, 2, Anhydrite, , 
#DBD6BC, 3, Heterolithic, Grey, 
#FF4C4A, 2, Volcanic, , 
#86F0B6, 5, Conglomerate, , 
#FF96F6, 2, Halite, , 
#F2FF42, 4, Sandstone, Grey, F-M
#DBC9BC, 3, Heterolithic, Red, 
#A68374, 2, Siltstone, Grey, 
#A657FA, 3, Dolomite, , 
#FFD073, 4, Sandstone, Red, C-M
#A6D1FF, 3, Limestone, , 
#FFDBBA, 3, Sandstone, Red, VF-F
#FFE040, 4, Sandstone, Grey, C-M
#A1655A, 2, Siltstone, Red, 
#363434, 1, Coal, , 
#664A4A, 1, Mudstone, Red, 
#666666, 1, Mudstone, Grey, """

LEXICON = { 'lithology':[r'overburden', r'sandstone', r'siltstone', r'shale', r'mudstone',
                           r'limestone', r'dolomite',
                           r'salt', r'halite', r'anhydrite', r'gypsum', r'sylvite',
                           r'clay', r'mud', r'silt', r'sand', r'gravel', r'boulders',
                           ],
            'amount': [r'streaks?', r'veins?', r'stringers?', r'interbed(?:s|ded)?',
                        r'blotch(?:es)?', r'bands?', r'fragments?', r'impurit(?:y|ies)',
                        r'minor', r'some', r'abundant', r'rare', r'flakes?',
                        r'[-\.\d]+%'
                       ],
            'grainsize': [r'vf(?:-)?', r'f(?:-)?', r'm(?:-)?', r'c(?:-)?', r'vc',
                           r'very fine(?: to)?', r'fine(?: to)?', r'medium(?: to)?', r'coarse(?: to)?', r'very coarse',
                           r'v fine(?: to)?', r'med(?: to)?', r'med.(?: to)?', r'v coarse',
                           r'grains?', r'granules?', r'pebbles?', r'cobbles?', r'boulders?',
                          ],
            'colour': [r"red(?:dish)?",
                        r"gray(?:ish)?",
                        r"grey(?:ish)?",
                        r"black(?:ish)?",
                        r"whit(?:e|ish)",
                        r"blu(?:e|ish)",
                        r"purpl(?:e|ish)",
                        r"yellow(?:ish)?",
                        r"green(?:ish)?",
                        r"brown(?:ish)?",
                        r"light", "dark",
                        r"sandy"
                        ],
            'synonyms': {'Overburden': ['Drift'],
                         'Anhydrite': ['Gypsum'],
                         'Salt': ['Halite', 'Sylvite'],
                        },
            'parts_of_speech': {'noun': ['lithology'],
                    'adjective': ['colour', 'grainsize'],
                    'subordinate': ['amount'],
                    },
            'abbreviations': ABBREVIATIONS
            }
