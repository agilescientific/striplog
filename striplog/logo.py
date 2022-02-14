import pathlib

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from .striplog import Striplog, Legend


def plot(fname=None, font_path=None):
    """
    Plots the Striplog logo.
    Requires Snare Drum font, by Nate Halley.

    Args:
        fname (str): Filename to save the plot to.
        font_path (str): Path to the font file.

    Returns:
        matplotlib.figure.Figure: The figure object.
    """
    csv_string = """top, base, comp lithology
    0,   5, Shale
    5,   9, Limestone
    9,  28, Conglomerate
    28, 32, Sandstone
    32, 36, Conglomerate
    36, 51, Sandstone
    51, 57, Siltstone
    57, 65, Shale
    65, 68, Mudstone
    68, 71, Shale
    71, 83, Mudstone
    83, 95, Shale
    95,100, Mudstone
    """
    strip = Striplog.from_csv(text=csv_string)

    l = u"""colour, width, component lithology
    #feec97, 6, Sandstone
    #fdd218, 7, Conglomerate
    #c6b259, 5, Siltstone
    #3ab4ff, 5, Limestone
    #d2d2d2, 5, Mudstone
    #909090, 4, Shale"""
    legend = Legend.from_csv(text=l)

    if font_path is None:
        raise RuntimeError('You need to provide the path to the font.')
    else:
        path = pathlib.Path(font_path)/'SDONE_0.ttf'

    # Make the plot.
    fig, ax = plt.subplots(figsize=(5, 5))
    strip.plot(ax=ax, legend=legend, aspect=1)
    prop = fm.FontProperties(fname=path)
    ax.text(0.1, 24.1, 'striplog', fontproperties=prop, size=99, color='k')
    ax.axis('off')

    if fname is not None:
        fig.savefig(fname, dpi=200)

    plt.close()
    return fig
