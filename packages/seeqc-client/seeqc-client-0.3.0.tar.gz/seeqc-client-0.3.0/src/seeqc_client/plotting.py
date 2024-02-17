import os

import matplotlib as mpl
import matplotlib.image as image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def _calculate_logo_position(data: dict) -> tuple:
    """Work out where logo should sit relative to data"""
    count = len(data.keys())
    if list(data.values())[-1] > 0.8:
        return 0.1, 0.9
    return (count-1)+0.1, 0.9


def _get_logo_path() -> str:
    """return path of Seeqc logo"""
    from src import seeqc_client
    path = os.path.dirname(seeqc_client.__file__)
    return path+r'\black_logo.png'


def plot(data: dict):
    """plot results histogram"""
    mpl.rcParams["font.family"] = "Consolas"
    file = _get_logo_path()
    seeqc = image.imread(file)
    imagebox = OffsetImage(seeqc, zoom=0.04)
    position = _calculate_logo_position(data)
    ab = AnnotationBbox(imagebox, position, frameon=False, xycoords='data')
    names = list(data.keys())
    values = list(data.values())
    fig = plt.bar(range(len(data)), values, tick_label=names, color='black')
    ax = plt.gca()
    ax.set_facecolor("#e4e4e3")
    ax.set_ylim([0, 1])
    ax.grid(axis='y', linestyle=(0, (3, 5)))
    ax.set_axisbelow(True)
    ax.set_ylabel('Populations')
    plt.yticks(np.arange(0, 1.1, 0.1))
    ax.add_artist(ab)
    plt.show()
