import pandas as pd
import upsetplot
import gzip
from collections import Counter
from itertools import compress
from matplotlib import pyplot


def count_scores(pk_results, genomes, exclusive=False):
    """Compute score counts for input to upsetplot

    Parameters
    ----------
    pk_results : PKResults
        PKResults object representing superset index
    genomes
        iterable of genomes included in subset
    """

    genomes_ordered = tuple(g for g in pk_results.genomes if g in genomes)
    genomes_set = set(genomes)
    counts = {}
    for b, n in Counter(score for _, score in pk_results).items():
        expanded_score = pk_results.decode_score(b)
        if exclusive and bool(
            set(compress(pk_results.genomes, expanded_score)) - genomes_set
        ):
            continue
        membership = tuple(
            sorted(
                set(compress(pk_results.genomes, expanded_score)).intersection(
                    genomes_set
                )
            )
        )
        if membership:
            counts[membership] = counts.get(membership, 0) + n
    return pd.Series(
        counts.values(),
        index=pd.MultiIndex.from_tuples(
            (tuple(g in k for g in genomes_ordered) for k in counts.keys()),
            names=genomes_ordered,
        ),
    )


def upset(
    pk_results,
    output,
    genomes,
    vertical=False,
    show_counts=False,
    min_subset_size=None,
    max_subset_size=None,
    exclusive=False,
    table=None,
):
    score_counts = count_scores(pk_results, genomes, exclusive=exclusive)
    if table:
        with (gzip.open if table.endswith(".gz") else open)(table, "wb") as f:
            score_counts.to_csv(f, sep="\t", header=["k-mers"])
    upsetplot.plot(
        score_counts,
        orientation="vertical" if vertical else "horizontal",
        show_counts=show_counts,
        min_subset_size=min_subset_size,
        max_subset_size=max_subset_size,
    )
    pyplot.savefig(output)
