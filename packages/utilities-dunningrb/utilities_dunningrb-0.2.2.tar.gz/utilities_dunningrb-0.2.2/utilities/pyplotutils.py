"""Define utilities that work with matplotlib.pyplot.
"""
from __future__ import annotations

import logging.config
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as pyplot
import numpy

from utilities.genutils import convert_to_type
from decorators.timing import timing

logger = logging.getLogger(__name__)
matplotlib.use("TkAgg")


@timing
def plotdata(
    *,
    data: numpy.ndarray,
    dependent_params: dict,
    independent_params: dict,
    title: str,
    show_plot_time: int | None = None,
    filepath: Path | None = None,
) -> None:
    """Plot the given data based on the plot indexes, y_limits and x_limits.

    Notes:
        (1) dependent_params must contain keyword "columns" mapping to a list of integers.

        (2) independent_params must contain keyword "column" mapping to an integer. The specified
        column will be plotted as the independent variable.

        (3) The greatest integer in dependent_params "columns" list must not be greater than the
        number of columns in the data. The columns specified will be plotted as dependent
        variables, all overlaid on the same plot.

        (4) ylim and xlim are each a list of two real numbers, specifying the upper
        and lower limits displayed on the plot for the x and y axes.

        (5) Optional show_plot_time provides the integer number of seconds to display the plot
        in a separate window before closing the window and returning control to the
        interpreter. If this parameter is not provided, the plot window is not generated.

        (6) Optional filepath provides string or Path object specifying the path to which an image
        of the plot should be saved. If this parameter is not provided, no file is saved.

        (7) If both show_plot_time and filepath are not provided, nothing is done.
    """
    if data is None or (show_plot_time is None and filepath is None):
        logger.warning(
            f"show_plot_time: {show_plot_time}; filepath: {filepath}--- NOTHING TO DO."
        )
        return

    pyplot.figure(num=1, dpi=150, figsize=(8, 5))
    pyplot.rcParams["font.family"] = "serif"
    pyplot.rcParams["figure.facecolor"] = "white"
    pyplot.rcParams["savefig.facecolor"] = "white"

    dep_cols = dependent_params["columns"]
    dep_axis_label = dependent_params["axis_label"]
    dep_labels = dependent_params["curve_labels"]
    dep_lims = dependent_params["lims"]

    ind_col = independent_params["column"]
    ind_axis_label = independent_params["axis_label"]
    ind_lims = independent_params["lims"]

    dep_cols = convert_to_type(dep_cols, list)
    dep_labels = convert_to_type(dep_labels, list)

    ind_vals = [d[ind_col] for d in data]

    for dep_col, dep_label in zip(dep_cols, dep_labels):
        dep_vals = [d[dep_col] for d in data]
        pyplot.plot(ind_vals, dep_vals, label=dep_label, markersize=1.25)

    pyplot.title(title)
    pyplot.legend(loc="lower right")
    pyplot.grid(True, color="lightgray")
    pyplot.ylabel(dep_axis_label)
    pyplot.xlabel(ind_axis_label)
    pyplot.ylim(dep_lims)
    pyplot.xlim(ind_lims)

    if show_plot_time is not None:
        logger.info(f"Displaying plot for {show_plot_time} seconds.")
        pyplot.show(block=False)
        time.sleep(show_plot_time)

    if filepath is not None:
        pyplot.savefig(filepath, transparent=False, bbox_inches="tight")
        logger.info(f"Figure saved to file: {filepath}.")
