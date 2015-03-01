#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines some default values for parsing cuttings descriptions.

:copyright: 2015 Agile Geoscience
:license: Apache 2.0
"""

ROCKS = [r'overburden', r'sandstone', r'siltstone', r'shale', r'mudstone',
         r'limestone', r'dolomite',
         r'salt', r'halite', r'anhydrite', r'gypsum', r'sylvite',
         r'clay', r'mud', r'silt', r'sand', r'gravel', r'boulders',
         ]

AMOUNTS = [r'streaks?', r'veins?', r'stringers?', r'interbed(?:s|ded)?',
           r'blotch(?:es)?', r'bands?', r'fragments?', r'impurit(?:y|ies)',
           r'minor', r'some', r'abundant', r'rare', r'flakes?',
           r'[-\.\d]+%'
           ]

GRAINSIZES = [r'vf', r'f', r'm', r'c', r'vc',
              r'very fine', r'fine', r'medium', r'coarse', r'very coarse',
              r'v fine', r'med', r'med.', r'v coarse',
              r'grains?', r'granules?', r'pebbles?', r'cobbles?', r'boulders?',
              ]

COLOURS = [r"red(?:dish)?",
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
           ]

SYNONYMS = {'Overburden': ['Drift'],
            'Anhydrite': ['Gypsum'],
            'Salt': ['Halite', 'Sylvite'],
            }
