from pankmer.version import __version__
from pankmer.pankmer import PKResults, index_wrapper
from pankmer.collect import collect
from pankmer.adjacency_matrix import get_adjacency_matrix
from pankmer.clustermap import clustermap
from pankmer.anchor import anchor_region, anchor_genome
from pankmer.env import KMER_SIZE

K = KMER_SIZE
