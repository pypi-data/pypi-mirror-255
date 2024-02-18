import itertools
import tarfile
from os import listdir
from os.path import isfile, join, isdir, exists

SEQ_EXTENSIONS = (
    ".fasta.gz",
    ".fna.gz",
    ".fa.gz",
    ".fastq.gz",
    ".fq.gz",
    ".fasta",
    ".fna",
    ".fa",
    ".fastq",
    ".fq",
)


def parse_genomes_input(genomes_input):
    if not isinstance(genomes_input, (tuple, list)):
        genomes_input = (
            list(genomes_input) if isinstance(genomes_input, set) else [genomes_input]
        )
    if (
        len(genomes_input) == 1
        and isfile(genomes_input[0])
        and tarfile.is_tarfile(genomes_input[0])
    ):
        input_is_tar = True
        with tarfile.open(genomes_input[0]) as tar:
            genomes = [tarinfo.name for tarinfo in tar if tarinfo.isreg()]
    else:
        input_is_tar = False
        genomes = list(
            itertools.chain.from_iterable(
                ([join(g, f) for f in sorted(listdir(g))] if isdir(g) else [g])
                for g in genomes_input
            )
        )
        # Check if input files exist and are files
        for genome in genomes:
            if not exists(genome) or not isfile(genome):
                raise RuntimeError(f"{genome} does not exist or is not a file!")
    return genomes_input, genomes, input_is_tar


def remove_seq_ext(genome):
    for ext in SEQ_EXTENSIONS:
        if genome.endswith(ext):
            genome = genome[: -1 * len(ext)]
    return genome
