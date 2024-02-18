from __future__ import annotations

import logging

import matplotlib.pyplot as plt
from pyg4ometry.visualisation import VtkViewer

from .base import HPGe
from .p00664b import P00664B
from .v02160a import V02160A


def plot_profile(
    hpge: HPGe, axes: plt.Axes = None, **kwargs
) -> tuple[plt.Figure, plt.Axes]:
    """Plot the HPGe profile with :mod:`matplotlib`.

    Parameters
    ----------
    hpge
        detector.
    axes
        pre-existing axes where the profile will be plotted.
    **kwargs
        any keyword argument supported by :func:`matplotlib.pyplot.plot`.

    """
    # data
    if isinstance(hpge, (V02160A, P00664B)):
        r = hpge.solid.obj1.pR
        z = hpge.solid.obj1.pZ
        logging.warning("The detector profile is that of the solid without cut")
    else:
        r = hpge.solid.pR
        z = hpge.solid.pZ

    x = r + [-x for x in reversed(r)]
    y = z + list(reversed(z))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    fig = None
    if axes is None:
        fig, axes = plt.subplots()
        fig.tight_layout()
        axes.axis("equal")
        axes.set_xlabel("r [mm]")
        axes.set_ylabel("z [mm]")
        axes.grid()

    default_kwargs = {
        "marker": "o",
        "markersize": 3,
        "markeredgecolor": colors[1],
        "markerfacecolor": colors[1],
        "linewidth": 2,
    }
    default_kwargs |= kwargs

    axes.plot(x, y, **default_kwargs)

    return fig, axes


def visualize(hpge: HPGe, viewer: VtkViewer = None) -> VtkViewer:
    """Visualize the HPGe with :class:`pyg4ometry.visualisation.VtkViewer`.

    Parameters
    ----------
    viewer
        pre-existing VTK viewer.
    """
    if viewer is None:
        viewer = VtkViewer()
    viewer.addLogicalVolume(hpge)
    viewer.setSurface()
    viewer.view(interactive=True)

    return viewer
