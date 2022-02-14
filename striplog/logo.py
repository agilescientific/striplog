import pathlib

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from .striplog import Striplog, Legend


def plot(fname=None, font_path=None):
    """
    Plots the Striplog logo.
    Requires Snare Drum font, by Nate Halley.
    """
    csv_string = """top, base, comp lithology
    0,  13, Shale
    13, 17, Limestone
    17, 28, Conglomerate
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
        raise RuntimeException('You need to provide the path to the font.')
    else:
        path = pathlib.Path(font_path)/'SDONE_0.ttf'

    # Make the plot.
    fig, ax = plt.subplots(figsize=(5, 5))
    strip.plot(ax=ax, legend=legend, aspect=1)
    prop = fm.FontProperties(fname=path)
    for i, letter in enumerate('striplog'):
        ax.text(0.1, 15 + 11.5*i, letter, fontproperties=prop, size=82)
    ax.axis('off')

    if fname is not None:
        fig.savefig(fname, dpi=200)

    plt.close()
    return fig
