from pankmer.index import print_err, generate_mem_blocks, measure_genomes
from os.path import commonprefix, basename
from itertools import chain
from more_itertools import batched

from pankmer.version import __version__
from pankmer.parse_genomes_input import parse_genomes_input, remove_seq_ext
from pankmer.env import KMER_SIZE


def dryrun(
    genomes_input=None,
    genomes_input_paired=None,
    kmer_size: int = KMER_SIZE,
    split_memory: int = 1,
    threads: int = 1,
) -> dict:
    """Perform a dry run of indexing and return the metadata

    Parameters
    ----------
    genomes_input
        paths to input genomes, directories, or tar file
    genomes_input
        paths to input genomes or directory (paired)
    split_memory : int
        number of memory blocks per thread
    threads : int
        number of threads

    Returns
    -------
    dict
        index metadata
    """

    if genomes_input is None and genomes_input_paired is None:
        raise RuntimeError("genomes must be provided")
    print_err("Recording genome sizes")
    if genomes_input is not None:
        genomes_input, genomes, input_is_tar = parse_genomes_input(genomes_input)
        genomes_dict = measure_genomes(
            genomes, str(genomes_input[0]) if input_is_tar else ""
        )
    else:
        genomes_dict, genomes, input_is_tar = {}, [], False
    if genomes_input_paired is not None:
        genomes_input_paired, genomes_paired, _ = parse_genomes_input(
            genomes_input_paired
        )
        genomes_dict_paired = {
            commonprefix([g0, g1]): s0 + s1
            for ((g0, s0), (g1, s1)) in batched(
                sorted(measure_genomes(genomes_paired, "").items()), 2
            )
        }
    else:
        genomes_dict_paired, genomes_paired = {}, []
    mem_blocks = generate_mem_blocks(split_memory, threads)
    all_core_blocks = []
    for m in range(1, len(mem_blocks)):
        temp_core_block = [mem_blocks[m - 1][-1]]
        for i in range(len(mem_blocks[m])):
            temp_core_block.append(mem_blocks[m][i])
            all_core_blocks.append(temp_core_block)
            temp_core_block = [mem_blocks[m][i]]
    return {
        "kmer_size": kmer_size,
        "version": __version__,
        "genomes": {
            c: remove_seq_ext(basename(g))
            for c, g in enumerate(
                chain(
                    genomes,
                    (commonprefix([g0, g1]) for g0, g1 in batched(genomes_paired, 2)),
                )
            )
        },
        "genome_sizes": {
            remove_seq_ext(basename(g)): s
            for g, s in chain(genomes_dict.items(), genomes_dict_paired.items())
        },
        "positions": {},
        "mem_blocks": all_core_blocks,
    }
