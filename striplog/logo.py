import pathlib
import os

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

from .striplog import Striplog, Legend


def plot(fname=None):
    """
    Plots the Striplog logo.
    Requires Snare Drum font, by Nate Halley.

    Args:
        fname (str): Filename to save the plot to.

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
                    95,100, Mudstone"""
    strip = Striplog.from_csv(text=csv_string)

    l = u"""colour, width, component lithology
            #feec97, 6, Sandstone
            #fdd218, 7, Conglomerate
            #c6b259, 5, Siltstone
            #3ab4ff, 5, Limestone
            #d2d2d2, 5, Mudstone
            #909090, 4, Shale"""
    legend = Legend.from_csv(text=l)

    # Read the file. NB This is not ZIP-safe.
    here = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    im = plt.imread(here / 'striplog_logotype.png')
    im[im==0] = np.nan

    # Make the plot.
    fig, ax = plt.subplots(figsize=(5, 5))

    strip.plot(ax=ax, legend=legend, aspect=1)
    ax.axis('off')

    logo_ax = fig.add_axes([0.162, 0.585, 0.7, 0.2], anchor='NE', zorder=1, facecolor='none')
    logo_ax.imshow(im, cmap='gray', interpolation='none')
    logo_ax.axis('off')

    if fname is not None:
        fig.savefig(fname, dpi=200)

    plt.close()

    return fig
