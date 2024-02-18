import pandas as pd
import seaborn as sns
from pankmer.tree import (
    adj_to_jaccard,
    adj_to_overlap,
    compute_linkage_matrix,
    adj_to_qv,
    adj_to_qv_symmetric,
    adj_to_ani,
)


def clustermap(
    adj_matrix,
    output: str,
    cmap: str = "mako_r",
    width: float = 7.0,
    height: float = 7.0,
    metric="ani",
    method="complete",
    optimal_ordering: bool = True,
    square: bool = True,
    heatmap_tick_pos="right",
    cbar_tick_pos="left",
    dendrogram_ratio: float = 0.2,
    dendrogram_spacer: float = 0.1,
):
    """Plot a clustered heatmap of genome similarity values

    Parameters
    ----------
    adj_matrix : DataFrame
        a Pandas data frame representing the adjacency matrix
    output : str
        path to destination file for plot
    cmap : str
        color map for the heatmap
    width : float
        width of the plot in inches
    height : float
        height of the plot in inches
    metric : str
        similarity metric to use for clustering. must be "intersection",
        "jaccard", "overlap", "qv", "qv_symmetric", or "ani" [ani]
    method : str
        linkage algorithm for hierarchical clustering. See
        `scipy.cluster.hierarchy.linkage` for details.
    optimal_ordering : bool
        If True, the linkage matrix will be reordered so that the distance
        between successive leaves is minimal. See
        `scipy.cluster.hierarchy.linkage`
    square : bool
        If True, the heatmap will be drawn square. This may force the figure
        dimensions to be altered slightly
    heatmap_tick_pos: str
        Position of heatmap ticks. Must be "left" or "right" [right]
    cbar_tick_pos : str
        Position of color bar ticks. Must be "left" or "right" [left]
    dendrogram_ratio : float
        Fraction of plot width used for dendrogram [0.2]
    dendrogram_spacer : float
        Fraction of plot width used as spacer between dendrogram and heatmap [0.1]
    """

    if metric == "jaccard":
        adj_matrix = adj_to_jaccard(adj_matrix)
    elif metric == "overlap":
        adj_matrix = adj_to_overlap(adj_matrix)
    elif metric == "qv":
        adj_matrix = adj_to_qv(adj_matrix)
    elif metric == "qv_symmetric":
        adj_matrix = adj_to_qv_symmetric(adj_matrix)
    elif metric == "ani":
        adj_matrix = adj_to_ani(adj_matrix)
    elif metric == "intersection":
        pass
    else:
        raise RuntimeError("invalid metric")
    link = compute_linkage_matrix(
        adj_matrix, method=method, optimal_ordering=optimal_ordering
    )
    ax = sns.clustermap(
        adj_matrix,
        cmap=cmap,
        figsize=(width, height),
        row_linkage=link,
        col_linkage=link,
        xticklabels=False,
        dendrogram_ratio=(dendrogram_ratio, 0),
    )
    if square:
        ax.ax_heatmap.set_aspect("equal")
    ax.ax_col_dendrogram.set_visible(False)
    ax_hm_pos = ax.ax_heatmap.get_position()
    ax_row_pos = ax.ax_row_dendrogram.get_position()
    match heatmap_tick_pos:
        case "left":
            ax.ax_heatmap.set_position(
                [0.9 - ax_hm_pos.width, ax_hm_pos.y0, ax_hm_pos.width, ax_hm_pos.height]
            )
        case "right":
            ax.ax_heatmap.set_position(
                [ax_hm_pos.x0 - 0.1, ax_hm_pos.y0, ax_hm_pos.width, ax_hm_pos.height]
            )
    ax.ax_heatmap.yaxis.set_ticks_position(heatmap_tick_pos)
    ax.ax_heatmap.set_yticklabels(ax.ax_heatmap.get_yticklabels(), rotation=0)
    ax.ax_row_dendrogram.set_position(
        [
            ax_row_pos.x0,
            ax_hm_pos.y0,
            ax_row_pos.width - dendrogram_spacer,
            ax_hm_pos.height,
        ]
    )
    ax.ax_cbar.set_position([0.97, ax_hm_pos.y0, 0.03, ax_hm_pos.height])
    ax.ax_cbar.yaxis.set_ticks_position(cbar_tick_pos)
    ax.savefig(output)
