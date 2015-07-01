# -*- coding: utf 8 -*-
"""
Define a suite a tests for the Striplog module.
"""

import numpy as np

from striplog import Component
from striplog import Interval
from striplog import Legend
from striplog import Striplog


def test_striplog():

    r1 = Component({'lithology':'sand'})
    r2 = Component({'lithology':'shale'})
    r3 = Component({'lithology':'limestone'})

    # Bottom up: elevation order
    iv1 = Interval(120, 100, components=[r1])
    iv2 = Interval(150, 120, components=[r2])
    iv3 = Interval(180, 160, components=[r1, r2])
    iv4 = Interval(200, 180, components=[r3, r2])

    s = Striplog([iv1, iv2, iv3, iv4])
    assert s.order == 'elevation'
    assert len(s) == 4
    assert s.start == 100
    assert s.stop == 200

    # Top down: depth order
    iv1 = Interval(80, 120, components=[r1])
    iv2 = Interval(120, 150, components=[r2])
    iv3 = Interval(180, 200, components=[r1, r2])
    iv4 = Interval(200, 250, components=[r3, r2])

    s = Striplog([iv1, iv2, iv3, iv4])
    assert s.order == 'depth'
    assert len(s) == 4
    assert s.start == 80
    assert s.stop == 250

def test_from_image():
    legend = Legend.default()
    imgfile = "tutorial/M-MG-70_14.3_135.9.png"
    striplog = Striplog.from_img(imgfile, 200, 300, legend=legend)
    assert len(striplog) == 26
    assert striplog[-1].primary.summary() == 'Volcanic'
    assert np.floor(striplog.find('sandstone').cum) == 15
    assert striplog.depth(260).primary.lithology == 'siltstone'
    assert striplog.to_las3() is not ''
    
    rock = striplog.find('sandstone')[1].components[0]
    assert rock in striplog

def from_csv():
    lexicon = Lexicon.default()
    csv_string = """  200.000,  230.329,  Anhydrite                                       
                      230.329,  233.269,  Grey vf-f sandstone                             
                      233.269,  234.700,  Anhydrite                                       
                      234.700,  236.596,  Dolomite                                        
                      236.596,  237.911,  Red siltstone                                   
                      237.911,  238.723,  Anhydrite                                       
                      238.723,  239.807,  Grey vf-f sandstone                             
                      239.807,  240.774,  Red siltstone                                   
                      240.774,  241.122,  Dolomite                                        
                      241.122,  241.702,  Grey siltstone                                  
                      241.702,  243.095,  Dolomite                                        
                      243.095,  246.654,  Grey vf-f sandstone                             
                      246.654,  247.234,  Dolomite                                        
                      247.234,  255.435,  Grey vf-f sandstone                             
                      255.435,  258.723,  Grey siltstone                                  
                      258.723,  259.729,  Dolomite                                        
                      259.729,  260.967,  Grey siltstone                                  
                      260.967,  261.354,  Dolomite                                        
                      261.354,  267.041,  Grey siltstone                                  
                      267.041,  267.350,  Dolomite                                        
                      267.350,  274.004,  Grey siltstone                                  
                      274.004,  274.313,  Dolomite                                        
                      274.313,  294.816,  Grey siltstone                                  
                      294.816,  295.397,  Dolomite                                        
                      295.397,  296.286,  Limestone                                       
                      296.286,  300.000,  Volcanic                                        
                    """
    strip2 = Striplog.from_csv(csv_string, lexicon=lexicon)
    assert len(strip2.top) == 7
