import pandas as pd
from collections import Counter


def count_kmers(*pk_results, names=None):
    """Count total and diagnostic K-mers in one or more indexes

    Parameters
    ----------
    pk_results
        a PKResults object
    names
        an iterable of the names for each input index

    Returns
    -------
    DataFrame
        table of K-mer counts for each index
    """
    names = names or range(len(pk_results))
    max_score = max(pkr.number_of_genomes for pkr in pk_results)
    kmer_counts = pd.DataFrame(0, columns=names, index=range(1, max_score + 1))
    for pkr, name in zip(pk_results, names):
        for s, c in Counter(sum(pkr.decode_score(score)) for _, score in pkr).items():
            kmer_counts.loc[s, name] = c
    return kmer_counts
