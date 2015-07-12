# -*- coding: utf 8 -*-

import numpy as np
from scipy.interpolate import spline, bisplev, lagrange
import matplotlib.pyplot as plt

from striplog import Decor
from striplog import Component
from striplog import Striplog
from striplog import Legend

basepath = 'baseline'  # path where to put images

imgfile = "../tutorial/M-MG-70_14.3_135.9.png"

"""
Make Decor Test Image
"""

r = {'colour': 'grey',
     'grainsize': 'vf-f',
     'lithology': 'sand'}
rock = Component(r)

d = {'color': '#86F0B6',
     'component': rock,
     'width': 3}

decor = Decor(d)

decor.component.summary(fmt="{lithology} {colour} {grainsize}")

dfig = decor.plot(fmt="{lithology} {colour} {grainsize}")

dfig.savefig("baseline/decor_test.png", dpi=100)

"""
Make Striplog test image
"""
legend = Legend.default()

striplog = Striplog.from_img(imgfile, 14.3, 135.9, legend=legend)

sfig = striplog.thickest(n=5).plot(legend=legend)

sfig.savefig('baseline/striplog_test_image.png', dpi=100)
