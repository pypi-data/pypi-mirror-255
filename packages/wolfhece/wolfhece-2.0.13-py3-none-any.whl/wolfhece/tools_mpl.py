
from matplotlib.figure import Figure
from matplotlib.axes import Axes

def fontsize(ax:Axes, size:int):

    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(size)