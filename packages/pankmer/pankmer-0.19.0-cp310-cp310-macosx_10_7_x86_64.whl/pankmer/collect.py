# ===============================================================================
# collect.py
# ===============================================================================

"""Calculate and plot collection curves"""

# Imports ======================================================================

import os.path
import pandas as pd
import seaborn as sns
from collections import Counter
import numpy as np
from math import prod, floor
from itertools import cycle
from scipy.stats import hypergeom


# Constants ====================================================================

COL_COLOR_PALETTE = "mako_r"


# Functions ====================================================================


def col_values_conf(pk_results):
    pkr = pk_results
    sc_matrix = np.zeros((pkr.number_of_genomes, pkr.number_of_genomes))
    for _, score in pkr:
        s = pkr.decode_score(score)
        sc_matrix[sum(s) - 1, :] += np.array(s[::-1])
    sc_df = pd.DataFrame(
        sc_matrix,
        index=range(1, pkr.number_of_genomes + 1),
        columns=pkr.genomes,
    )
    g = len(sc_df.columns)
    coef_matrix_total = np.array(
        [
            [prod((g - s - i) / (g - 1 - i) for i in range(n)) for n in range(g)]
            for s in range(1, g + 1)
        ]
    )
    coef_matrix_core = np.flip(coef_matrix_total.copy(), axis=0)
    for n in range(1, g):
        coef_matrix_total[:, n] += coef_matrix_total[:, n - 1]
    col_df_core = pd.DataFrame(sc_df.transpose().dot(coef_matrix_core).transpose())
    col_df_total = pd.DataFrame(sc_df.transpose().dot(coef_matrix_total).transpose())
    col_df = pd.concat((col_df_total, col_df_core))
    col_df["Genomes"] = tuple(range(1, g + 1)) * 2
    plotting_data = col_df.melt(id_vars=["Genomes"], value_name="k-mers")
    del plotting_data["variable"]
    plotting_data["sequence"] = (("Pan",) * g + ("Core",) * g) * g
    return plotting_data


def col_values(pk_results, contours=None):
    """Calculate collection curve

    Parameters
    ----------
    pk_results
        a PKResults object
    contours
        if not None, an iterable of integers between 0 and 100

    Yields
    -------
        collection curve values
    """

    pkr = pk_results
    g = pkr.number_of_genomes
    score_dist = Counter(sum(pkr.decode_score(score)) for _, score in pkr)
    for n_genomes in range(1, g + 1):
        yield (
            n_genomes,
            sum(
                (1 - prod((g - s - n) / (g - n) for n in range(n_genomes)))
                * score_dist[s]
                for s in range(1, g + 1)
            ),
            "Pan",
        )
        if contours:
            for c in contours:
                yield (
                    n_genomes,
                    sum(
                        (hypergeom.sf(floor(c / 100 * n_genomes), g, s, n_genomes))
                        * score_dist[s]
                        for s in range(1, g + 1)
                    ),
                    f"{c}%",
                )
        yield (
            n_genomes,
            sum(
                prod((s - n) / (g - n) for n in range(n_genomes)) * score_dist[s]
                for s in range(1, g + 1)
            ),
            "Core",
        )


def col_plot(
    plotting_data,
    output,
    title: str = "Collection curve",
    linewidth: int = 3,
    palette=COL_COLOR_PALETTE,
    alpha: float = 1.0,
    width: float = 4.0,
    height: float = 3.0,
    legend_loc="best",
):
    """Draw a plot of the collection curve

    Parameters
    ----------
    plotting_data : DataFrame
        data frame of plotting data to be passed to sns.lineplot
    output
        path to output file
    title : str
        plot title [Collection curve]
    linewidth : int
        line width [3]
    palette
        argument sent to seaborn to be used as color palette [mako_r]
    alpha : float
        opacity of plot lines [1.0]
    width : float
        width of plot in inches [4.0]
    height : float
        height of plot in inches [3.0]
    legend_loc : str
        location of plot legend, e.g. 'upper left', 'best', or 'outside' [best]
    """

    ax = sns.lineplot(
        x="Genomes",
        y="k-mers",
        hue="sequence",
        data=plotting_data,
        linewidth=linewidth,
        palette=palette,
        alpha=alpha,
    )
    ax.set_title(title)
    ax.set_ylim(bottom=0)
    if legend_loc == "outside":
        leg = ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    else:
        leg = ax.legend(loc=legend_loc)
    for line in leg.get_lines():
        line.set_linewidth(linewidth)
        line.set_alpha(alpha)
    fig = ax.get_figure()
    fig.set_figwidth(width)
    fig.set_figheight(height)
    fig.tight_layout()
    fig.savefig(output)
    fig.clf()


def collect(
    pk_results,
    output=None,
    title: str = "Collection curve",
    linewidth: int = 3,
    palette=COL_COLOR_PALETTE,
    alpha=1,
    width=4,
    height=3,
    conf=False,
    contours=False,
    legend_loc="best",
):
    """Compute a collection curve, optionally drawing intermediate contours,
    or generating a plot, or computing confidence intervals (experimental)

    Parameters
    ----------
    plotting_data : DataFrame
        data frame of plotting data to be passed to sns.lineplot
    output
        path to output file
    title : str
        plot title [Collection curve]
    linewidth : int
        line width [3]
    palette
        argument sent to seaborn to be used as color palette [mako_r]
    alpha : float
        opacity of plot lines [1.0]
    width : float
        width of plot in inches [4.0]
    height : float
        height of plot in inches [3.0]
    conf : bool
        draw experimental confidence intervals
    contours : bool or list of int
        if not false, should be a list of intermediate contours in percent
        (e.g. [25, 50, 75])
    legend_loc : str
        location of plot legend, e.g. 'upper left', 'best', or 'outside' [best]
    """

    if conf:
        col_df = col_values_conf(pk_results)
    else:
        col_df = pd.DataFrame(
            col_values(pk_results, contours=contours),
            columns=("Genomes", "k-mers", "sequence"),
        )
    if output:
        col_plot(
            col_df,
            output,
            title=title,
            linewidth=linewidth,
            palette=(palette if contours else sns.color_palette(palette, n_colors=2)),
            alpha=alpha,
            width=width,
            height=height,
            legend_loc=legend_loc,
        )
    return col_df
