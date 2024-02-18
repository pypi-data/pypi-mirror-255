import pandas as pd
import os.path
import tarfile
from pankmer.index import get_adjacency_matrix as _get_adjacency_matrix

def get_adjacency_matrix(index):
    """Generate an adjacency matrix from a PKResults object

    Parameters
    ----------
    index : str
        path to a directory or tar file containing a PanKmer index

    Returns
    -------
    DataFrame
        an adjacency matrix
    """

    mat, genomes = _get_adjacency_matrix(
        str(index),
        str(index) if os.path.isfile(index) and tarfile.is_tarfile(index) else ""
    )
    return pd.DataFrame(mat, index=genomes, columns=genomes)
