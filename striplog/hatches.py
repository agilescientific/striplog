"""
Custom hatches for matplotlib. They have a geological flavour.

See https://github.com/agile-geoscience/striplog/issues/7 for details.

:copyright: 2016 Agile Geoscience
:license: Apache 2.0
"""
import matplotlib as mpl
from matplotlib.hatch import Shapes
from matplotlib.path import Path


# The hatches have to be registered with mpl.hatch to be recoginized.
# See the end of this file.

# But first we create the hatch classes themselves. Long winded.

class Crosses(Shapes):
    """
    Attempt at USGS pattern 712
    """
    def __init__(self, hatch, density):
        verts = [
            (0.8, 0.8),
            (0.0, 0.0),
            (0.0, 0.8),
            (0.8, 0.0),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count('c') * density
        self.size = 0.5

        super().__init__(hatch, density)


class Pluses(Shapes):
    """
    Attempt at USGS pattern 721, 327
    """
    def __init__(self, hatch, density):
        verts = [
            (0.4, 0.8),
            (0.4, 0.0),
            (0.0, 0.4),
            (0.8, 0.4),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count('p') * density
        self.size = 0.5

        super().__init__(hatch, density)


class Dashes(Shapes):
    """
    Attempt at USGS pattern 620
    """
    def __init__(self, hatch, density):
        verts = [
            (0., 0.),  # left, bottom
            (1., 0.),  # right, top
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count('=') * density
        self.size = 0.5

        super().__init__(hatch, density)


class Bricks(Shapes):
    """
    Attempt at USGS pattern 627
    """
    def __init__(self, hatch, density):
        verts = [
            (0.0, 0.0),
            (0.9, 0.0),
            (0.9, 0.95),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count('b') * density
        self.size = 1.0

        super().__init__(hatch, density)


class SlantBricks(Shapes):
    """
    Slanted version of Bricks.
    """
    def __init__(self, hatch, density):
        verts = [
            (0.0, 0.0),
            (1., 0.),
            (0.75, 1.),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("s") * density
        self.size = 1.0
        super().__init__(hatch, density)


class Ticks(Shapes):
    """
    Attempt at USGS pattern 230
    """
    def __init__(self, hatch, density):
        verts = [
            (0.0, 0.0),
            (0.0, 1.0),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("!") * density
        self.size = 1.0

        super().__init__(hatch, density)


class Ells(Shapes):
    """
    Attempt at USGS pattern 412
    """
    def __init__(self, hatch, density):
        verts = [
            (0.0, 0.0),
            (0.0, 0.5),
            (0.0, 0.0),
            (0.5, 0.0),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("l") * density
        self.size = 1.0

        super().__init__(hatch, density)


class Triangles(Shapes):
    """
    Triangles.
    """
    def __init__(self, hatch, density):
        verts = [
            (0.250, 0.5),
            (0., 0.),
            (0.5, 0.),
            (0.25, 0.5),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("t") * density
        self.size = 1.0
        super().__init__(hatch, density)


class Vees(Shapes):
    """
    Attempt at USGS pattern 731
    """
    def __init__(self, hatch, density):
        verts = [
            (0.250, 0.0),
            (0., 0.5),
            (0.25, 0.),
            (0.5, 0.5),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("v") * density
        self.size = 1.0

        super().__init__(hatch, density)


class InvertedVees(Shapes):
    """
    Inverted version of Vees.
    """
    def __init__(self, hatch, density):
        verts = [
            (0.250, 0.5),
            (0., 0.),
            (0.25, 0.5),
            (0.5, 0.),
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.MOVETO,
                 Path.LINETO,
                 ]

        path = Path(verts, codes, closed=False)

        self.shape_vertices = path.vertices
        self.shape_codes = path.codes
        self.num_rows = hatch.count("^") * density
        self.size = 1.0
        super().__init__(hatch, density)


# Register custom hatches
mpl.hatch._hatch_types.append(Crosses)
mpl.hatch._hatch_types.append(Pluses)
mpl.hatch._hatch_types.append(Dashes)
mpl.hatch._hatch_types.append(Bricks)
mpl.hatch._hatch_types.append(SlantBricks)
mpl.hatch._hatch_types.append(Ticks)
mpl.hatch._hatch_types.append(Ells)
mpl.hatch._hatch_types.append(Triangles)
mpl.hatch._hatch_types.append(Vees)
mpl.hatch._hatch_types.append(InvertedVees)
