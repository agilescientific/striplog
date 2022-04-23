"""
Define a suite a tests for the Striplog module.
"""
import numpy as np
import pytest

from striplog import Component
from striplog import Interval
from striplog import Legend
from striplog import Lexicon
from striplog import Striplog
from striplog.striplog import StriplogError

las3 = """~Lithology_Parameter
LITH .   Striplog         : Lithology source          {S}
LITHD.   MD               : Lithology depth reference {S}

~Lithology_Definition
LITHT.M                   : Lithology top depth       {F}
LITHB.M                   : Lithology base depth      {F}
LITHD.                    : Lithology description     {S}

~Lithology_Data | Lithology_Definition
  280.000,  299.986,  "Red, siltstone"
  299.986,  304.008,  "Grey, sandstone, vf-f"
  304.008,  328.016,  "Red, siltstone"
  328.016,  328.990,  "Limestone"
  328.990,  330.007,  "Red, siltstone"
  330.007,  333.987,  "Limestone"
  333.987,  338.983,  "Red, siltstone"
  338.983,  340.931,  "Limestone"
  340.931,  345.927,  "Red, siltstone"
  345.927,  346.944,  "Limestone"
  346.944,  414.946,  "Red, siltstone"
  414.946,  416.936,  "Grey, mudstone"
  416.936,  422.440,  "Red, heterolithic"
  422.440,  423.414,  "Grey, mudstone"
 """

csv_intervals = """   200.000,  230.329,  Anhydrite
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

csv_points = """top, porosity
                1200, 6.4
                1205, 7.3
                1210, 8.2
                1250, 9.2
                1275, 4.3
                1300, 2.2"""

lappy_list = [Interval(**{'top': 50,
                                  'base': 60,
                                  'components': [Component({'lithology': 'dolomite'}),]}),
                      Interval(**{'top': 55,
                                  'base': 75,
                                  'components': [Component({'lithology': 'limestone'}),]}),
                      Interval(**{'top': 75,
                                  'base': 80,
                                  'components': [Component({'lithology': 'volcanic'}),]}),
                      Interval(**{'top': 78,
                                  'base': 90,
                                  'components': [Component({'lithology': 'anhydrite'}),]})
                      ]

top_dict = {'Ardmore': 2510.03,
            'Cody': 2521.61,
            'Sussex Upper Top': 2521.61,
            'Sussex Lower Top': 2527.71,
            'Sussex Lower Base': 2528.62,
            'Sussex Upper Base': 2529.54,
            'Niobrara': 2530.75
           }

data_dict = {'top': [70.273, 70.744],
             'facies': [3, 0],
             'description': ['brown shale with interbedded sandstone pebbles', 'cyrstalline dolomite'],
            }


def test_error():
    """Test the generic error.
    """
    with pytest.raises(StriplogError):
        Striplog([])


def test_striplog():
    """Test most of the things.
    """
    r1 = Component({'lithology': 'sand'})
    r2 = Component({'lithology': 'shale'})
    r3 = Component({'lithology': 'limestone'})

    # Bottom up: elevation order
    iv1 = Interval(120, 100, components=[r1])
    iv2 = Interval(150, 120, components=[r2])
    iv3 = Interval(180, 160, components=[r1, r2])
    iv4 = Interval(200, 180, components=[r3, r2])

    s1 = Striplog([iv1, iv2])
    s2 = Striplog([iv3, iv4])
    s = s1 + s2
    assert s.order == 'elevation'
    assert len(s) == 4
    assert s.start.z == 100
    assert s.stop.z == 200
    assert s.__repr__() != ''
    assert s.__str__() != ''

    s_rev = s.invert(copy=True)
    assert s_rev.order == 'depth'
    x = s.invert()
    assert x is None
    assert s.order == 'depth'
    assert s[0].top.z == 100

    # Top down: depth order
    iv1 = Interval(80, 120, components=[r1])
    iv2 = Interval(120, 150, components=[r2])
    iv3 = Interval(180, 200, components=[r1, r2])
    iv4 = Interval(200, 250, components=[r3, r2])

    s = Striplog([iv1, iv2, iv3, iv4])
    assert s.order == 'depth'
    assert len(s) == 4
    assert s.start.z == 80
    assert s.stop.z == 250
    assert s._Striplog__strict()

    listy = [iv.thickness for iv in s]
    assert len(listy) == 4

    s[2] = Interval(180, 190, components=[r1, r2])
    assert len(s.find_gaps()) == 2

    # Crop.
    x = s.crop((110, 210), copy=True)
    assert x.start.z == 110

    # To csv
    csv = x.to_csv(header=True)
    assert csv[:3] == 'Top'

    # Add.
    assert len(s + iv4) == 5


def test_from_dict():
    """
    Test gen from dictionary.
    """
    striplog = Striplog.from_dict(top_dict)
    assert len(striplog) == 7
    assert striplog.thinnest().summary() == '0.00 m of Cody'


def test_descriptions_and_data():
    """Test that descriptions are parsed into Components when
    miscellaneous data is present.
    """
    strip = Striplog._build_list_of_Intervals(data_dict)
    assert len(strip[0].components[0]) == 2


def test_from_image():
    """Test the generation of a striplog from an image.
    """
    legend = Legend.builtin('NSDOE')
    imgfile = "tests/data/M-MG-70_14.3_135.9.png"
    striplog = Striplog.from_image(imgfile, 200, 300, legend=legend)
    assert len(striplog) == 26
    assert striplog[-1].primary.summary() == 'Volcanic'
    assert np.floor(striplog.find('sandstone').cum) == 15
    assert striplog.read_at(260).primary.lithology == 'siltstone'
    assert striplog.to_las3() != ''
    assert striplog.cum == 100.0
    assert striplog.thickest().primary.lithology == 'anhydrite'
    assert striplog.thickest(n=7)[1].primary.lithology == 'sandstone'
    assert striplog.thinnest().primary.lithology == 'dolomite'
    assert striplog.thinnest(n=7)[1].primary.lithology == 'siltstone'

    # To and from log.
    log, basis, table = striplog.to_log(step=0.1524, return_meta=True)
    assert log[5] == 2.0
    strip = Striplog.from_log(log, basis=basis, components=table)
    assert len(strip) == len(striplog)
    strip2 = Striplog.from_log(log, basis=basis, cutoff=3, legend=legend)
    assert len(strip2) == 18

    # Extract log onto striplog.
    striplog = striplog.extract(log, basis=basis, name="Log", function=np.mean)
    assert striplog[0].data['Log'] == 2.0

    # Indexing.
    indices = [2, 7, 20]
    del striplog[indices]
    assert len(striplog.find_gaps()) == len(indices)

    # Prune and anneal.
    striplog = striplog.prune(limit=1.0, keep_ends=True)
    assert len(striplog) == 14

    striplog = striplog.anneal()
    assert not striplog.find_gaps()  # Should be None

    striplog = striplog.merge_neighbours()
    assert len(striplog) == 11

    rock = striplog.find('sandstone')[1].components[0]
    assert rock in striplog

    # Anneal up or down
    s = striplog[[1, 3]]
    assert s.anneal(mode='up')[1].top.z == s[0].base.z
    assert s.anneal(mode='down')[0].base.z == s[1].top.z


def test_from_descriptions():
    """Test the CSV route.
    """
    lexicon = Lexicon.default()
    strip2 = Striplog.from_descriptions(text=csv_intervals, lexicon=lexicon)
    assert len(strip2.unique) == 7


def test_points():
    """Test a striplog of points.
    """
    points = Striplog.from_csv(text=csv_points, points=True)
    assert len(points) == 6
    assert points.order == 'none'


def test_from_las3():
    """Test the LAS3 route.
    """
    lexicon = Lexicon.default()
    s = Striplog.from_las3(las3, lexicon=lexicon)
    assert len(s) == 14


def test_from_array():
    """Test the array route.
    Deprecated.
    """
    lexicon = Lexicon.default()

    a = [(100, 200, 'red sandstone'),
         (200, 250, 'grey shale'),
         (200, 250, 'red sandstone with shale stringers'),
         ]

    with pytest.warns(DeprecationWarning):
        s = Striplog._from_array(a, lexicon=lexicon)

    assert s.__str__() != ''


def test_striplog_intersect():
    """Test intersection. This example is from the tutorial.
    """
    chrono = Striplog([Interval(**{'top': 0,
                                   'base': 60,
                                   'components': [Component({'age': 'Holocene'})]
                                   }),
                       Interval(**{'top': 60,
                                   'base': 75,
                                   'components': [Component({'age': 'Palaeogene'})]
                                   }),
                       Interval(**{'top': 75,
                                   'base': 100,
                                   'components': [Component({'age': 'Cretaceous'})]
                                   }),
                       ])
    legend = Legend.builtin('NSDOE')
    imgfile = "tests/data/M-MG-70_14.3_135.9.png"
    strip = Striplog.from_image(imgfile, 14.3, 135.9, legend=legend)
    sands = strip.find('sandstone')
    cretaceous = chrono.find('Palaeogene')
    cret_sand = sands.intersect(cretaceous)
    assert len(cret_sand) == 3
    assert cret_sand.stop.z == 75


def test_striplog_merge_overlaps():
    """Test merging. This example is from the tutorial.
    """
    lappy = Striplog(lappy_list)
    assert lappy.find_overlaps(index=True) == [0, 2]
    assert lappy.merge_overlaps() is None
    assert lappy.find_overlaps() is None


def test_striplog_merge():
    """Test new merging. This example is from the tutorial.
    """
    lappy = Striplog(lappy_list)
    assert len(lappy.merge('top')) == 4
    assert lappy.merge('top')[0].base.z == 55
    assert lappy.merge('top', reverse=True)[0].base.z == 60


def test_striplog_union():
    """Test union.
    """
    lappy = Striplog([Interval(**{'top': 0,
                                  'base': 60,
                                  'components': [Component({'lithology': 'dolomite'}),]}),
                      Interval(**{'top': 55,
                                  'base': 75,
                                  'components': [Component({'lithology': 'limestone'}),]}),
                      ])
    lippy = Striplog([Interval(**{'top': 0,
                                  'base': 30,
                                  'components': [Component({'lithology': 'marl'}),]}),
                      ])
    u = lappy.union(lippy)
    assert len(u) == 2
    assert len(u[0].components) == 2


def test_fill():
    gappy = Striplog([Interval(**{'top': 0,
                                  'base': 60,
                                  'components': [Component({'lithology': 'dolomite'}),]}),
                      Interval(**{'top': 65,
                                  'base': 75,
                                  'components': [Component({'lithology': 'limestone'}),]}),
                  ])

    f = gappy.fill(Component({'lithology': 'marl'}))
    assert len(f) == 3
    assert f[1].primary == Component({'lithology': 'marl'})

    f = gappy.fill()
    assert not f[1]


def test_histogram():
    """Test histogram. This example is from the tutorial.
    """
    lexicon = Lexicon.default()
    striplog = Striplog.from_las3(las3, lexicon=lexicon)
    thicks, *_ = striplog.histogram(plot=False)  # See test_plots for plots.
    t = [123.005, 7.919, 5.504, 4.022, 2.964]
    assert np.allclose(t, thicks)


def test_petrel():
    """Test we can load petrel text.
    """
    # What to include: only rows with Well = P-108
    include = {'Well': lambda x: x == 'P-108'}

    # Rename the Surface field as Name.
    remap = {'Surface': 'Name'}

    # What to exclude: any rows with Name = TD
    exclude = {'Name': lambda x: x == 'TD'}

    # What to transform before using.
    function = {'Z': lambda x: -x,
                'Name': lambda x: x.replace('Maguma', 'Meguma')}

    # Which fields to leave out of the result, apart from those that are Null.
    ignore = ['Edited by user',
              'Locked to fault',
              'Used by dep.conv.',
              'Well', 'Symbol']

    # Do the thing!
    s = Striplog.from_petrel("tests/data/petrel.dat",
                             include=include,
                             exclude=exclude,
                             remap=remap,
                             ignore=ignore,
                             function=function,
                             points=False,
                             null=-999.0
                             )

    print(s)

    assert len(s) == 4
    assert s[3].base.z == 1056
    assert s[3].data['Name'] == 'Meguma'
