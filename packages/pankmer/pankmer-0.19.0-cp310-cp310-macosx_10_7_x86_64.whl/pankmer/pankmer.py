import argparse
import gzip
import io
from os.path import join, isfile, isdir, basename, dirname, exists, commonprefix
from os import mkdir
import sys
import time
import pandas as pd
import math
import json
import shutil
import tarfile
from operator import itemgetter
from itertools import chain
from more_itertools import batched
from pankmer.index import (
    print_err,
    score_byte_to_blist,
    run_index,
    measure_genomes,
    load_metadata
)
from pankmer.env import EXAMPLE_DATA_DIR, KMER_SIZE
from pankmer.download import download_example
from pankmer.count import count_kmers
from pankmer.collect import COL_COLOR_PALETTE, collect
from pankmer.upset import upset
from pankmer.subset import subset
from pankmer.adjacency_matrix import get_adjacency_matrix
from pankmer.tree import (
    tree,
    adj_to_jaccard,
    adj_to_overlap,
    adj_to_qv,
    adj_to_qv_symmetric,
    adj_to_ani,
)
from pankmer.clustermap import clustermap
from pankmer.anchor import (
    COLOR_PALETTE,
    anchor_region,
    anchor_genome,
    anchor_genome_plot,
    anchor_heatmap,
)
from pankmer.anchormap import anchormap
from pankmer.dryrun import dryrun
from pankmer.version import __version__
from pankmer.parse_genomes_input import parse_genomes_input, remove_seq_ext

# ===============================================================================
KMER_MAX = 2**64 - 1

# ===============================================================================

class PKIterator:
    def __init__(self, results):
        self._results = results

    def __next__(self):
        kmer = self._results.get_kmer_byte()
        score = self._results.get_score_byte()
        if kmer == None or score == None:
            self._results.reset_iter()
            raise StopIteration
        return kmer, score


class PKResults:
    def __init__(self, results_dir: str, threads: int = 1):
        index_files = ["metadata.json", "kmers.bgz", "scores.bgz"]
        self.input_is_tar = False
        if isfile(results_dir) and tarfile.is_tarfile(results_dir):
            self.input_is_tar = True
            self.tar = tarfile.open(results_dir)
            found_files = {
                basename(tarinfo.name) for tarinfo in self.tar if tarinfo.isreg()
            }
            for file in index_files:
                if file not in found_files:
                    raise ValueError(f"{file} is not found in index!")
            kmers_filename, _, scores_filename = sorted(
                tarinfo.name for tarinfo in self.tar if tarinfo.isreg()
            )
            metadata = load_metadata(str(results_dir), str(results_dir))
            self.kmers_stream = gzip.open(self.tar.extractfile(kmers_filename), "rb")
            self.scores_stream = gzip.open(self.tar.extractfile(scores_filename), "rb")
        elif isdir(results_dir):
            for file in index_files:
                file_path = join(results_dir, file)
                if not isfile(file_path):
                    raise ValueError(f"{file} is not found in results directory!")
            metadata = load_metadata(str(results_dir), "")
            self.kmers_stream = gzip.open(join(results_dir, "kmers.bgz"), "rb")
            self.scores_stream = gzip.open(join(results_dir, "scores.bgz"), "rb")
        else:
            raise ValueError(f"{results_dir} is not a valid directory!")
        self.results_dir = results_dir
        self.kmer_size = metadata.kmer_size
        self.genomes = tuple(g for _, g in sorted(metadata.genomes.items()))
        self.number_of_genomes = len(self.genomes)
        self.positions = metadata.positions
        self.kmer_bitsize = math.ceil(self.kmer_size * 2 / 8)
        self.score_bitsize = math.ceil(len(self.genomes) / 8)
        self.threads = threads
        self.mem_blocks = metadata.mem_blocks 
        self.kmer_buffer = io.BufferedReader(self.kmers_stream)
        self.score_buffer = io.BufferedReader(self.scores_stream)

    def __iter__(self) -> PKIterator:
        """Object iterator

        Returns
        -------
        PKIterator
            returns a kmer and a score in bytes
        """
        return PKIterator(self)

    def get_kmer_byte(self) -> bytes:
        """read bytes in size of one kmer from kmers file

        Returns
        -------
        bytes
            bytes representing Kmer
        """
        kmer_byte = self.kmer_buffer.read(self.kmer_bitsize)
        if not kmer_byte:
            return None
        return kmer_byte

    def get_score_byte(self) -> bytes:
        """read bytes in size of one score from scores file

        Returns
        -------
        bytes
            bytes represting what samples have a Kmer
        """
        score_byte = self.score_buffer.read(self.score_bitsize)
        if not score_byte:
            return None
        return score_byte

    def seek_kmer(self, kmer_num: int):
        """Move Kmer file pointer past a number of Kmers

        Parameters
        ----------
        kmer_num : int
            Number of Kmers to skip
        """
        self.kmer_buffer.seek(kmer_num * self.kmer_bitsize)

    def seek_score(self, score_num: int):
        """Move Score file pointer past a number of scores

        Parameters
        ----------
        score_num : int
            Number of scores to skip
        """
        self.score_buffer.seek(score_num * self.score_bitsize)

    def reset_iter(self):
        """Move Kmer and Score files' pointers to 0 position"""
        self.seek_kmer(0)
        self.seek_score(0)

    def set_threads(self, threads: int):
        """Set number of threads to run multithreaded processes

        Parameters
        ----------
        threads : int
            Number of threads
        """
        self.threads = threads

    def decode_score(self, bits: bytes) -> list:
        """Convert score bytes to a list of binary flags


        Parameters
        ----------
        bits : bytes
            Score bytes generated by PanKmer indexing

        Returns
        -------
        list
            List of binary flags indicating if genome at position x has the corresponding Kmer
            0: Genome doesn't have Kmer
            1: Genome has Kmer
        """
        return score_byte_to_blist(bits, self.number_of_genomes)

    def close(self):
        self.kmers_stream.close()
        self.scores_stream.close()
        if self.input_is_tar:
            self.tar.close()


def index_wrapper(
    outdir: str,
    genomes_input=None,
    genomes_input_paired=None,
    split_memory: int = 1,
    threads: int = 1,
    index: str = "",
    fraction: float = 1.0,
    gzip_level: int = 6,
    k=KMER_SIZE,
):
    if k < 9:
        raise RuntimeError("k < 9 not allowed")
    if k > 31:
        raise RuntimeError("k > 31 not allowed")
    if k % 2 == 0:
        raise RuntimeError(f"even value of k ({k}) not allowed, please choose an odd value")
    if basename(outdir).endswith(".tar"):
        output_is_tar = True
        outdir = join(dirname(outdir), basename(outdir)[:-4])
    else:
        output_is_tar = False
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

    # Make the output directory if it doesn't exist
    if not exists(outdir):
        mkdir(outdir)

    total_seq_bp = sum(chain(genomes_dict.values(), genomes_dict_paired.values()))
    if total_seq_bp == 0:
        raise RuntimeError("No sequence in input")
    print_err(f"{total_seq_bp} bp of sequence total")
    print_err(f"Using {split_memory} memory blocks")
    positions_dictionary, mem_blocks = run_index(
        (str(genomes_input[0] if genomes_input else "") if input_is_tar else ""),
        (genomes if genomes else []),
        (genomes_paired if genomes_paired else []),
        str(outdir),
        split_memory=split_memory,
        threads=threads,
        index=index,
        input_is_tar=input_is_tar,
        fraction=fraction,
        gzip_level=gzip_level,
        kmersize=k,
    )
    print_err("Saving metadata.")
    metadata_dict = {
        "kmer_size": k,
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
        "positions": dict(sorted(positions_dictionary.items(), key=itemgetter(1))),
        "mem_blocks": mem_blocks,
        "fraction_cutoff": [fraction, int(fraction * KMER_MAX)],
    }
    with open(f"{outdir}/metadata.json", "w") as outfile:
        json.dump(metadata_dict, outfile)
    if output_is_tar:
        with tarfile.open(f"{outdir}.tar", "w") as tar:
            tar.add(outdir)
        shutil.rmtree(outdir)


def run_index_wrapper(args):
    if args.time:
        start = time.time()
    # index = args.index
    index_wrapper(
        args.output,
        genomes_input=args.genomes,
        genomes_input_paired=args.genomes_paired,
        split_memory=args.rounds,
        threads=args.threads,
        index="",
        k=args.kmer_size,
        fraction=1 - 10 ** (-1 * args.qual / (10 * args.kmer_size)) if args.qual else args.fraction,
        gzip_level=args.gzip_level,
    )
    if args.time:
        stop = time.time()
        print(f"Indexed in {(stop - start) / 60:.2f} minutes")


def run_count(args):
    kmer_counts = count_kmers(*(PKResults(i) for i in args.index), names=args.index)
    kmer_counts.to_csv(sys.stdout, sep="\t")


def run_collect(args):
    sat_df = collect(
        PKResults(args.index),
        args.output,
        title=args.title,
        width=args.width,
        height=args.height,
        palette=args.color_palette,
        alpha=args.alpha,
        linewidth=args.linewidth,
        conf=args.conf,
        contours=args.contours,
        legend_loc=args.legend_loc,
    )
    if args.table:
        sat_df.to_csv(args.table, sep="\t", index=False)


def run_upset(args):
    if args.time:
        start = time.time()
    upset(
        PKResults(args.input),
        args.output,
        args.genomes,
        vertical=args.vertical,
        show_counts=args.show_counts,
        min_subset_size=args.min_subset_size,
        max_subset_size=args.max_subset_size,
        exclusive=args.exclusive,
        table=args.table,
    )
    if args.time:
        stop = time.time()
        print(f"UpSet plot generated in {(stop - start) / 60:.2f} minutes")


def run_subset(args):
    if args.time:
        start = time.time()
    subset(
        args.input,
        args.output,
        args.genomes,
        exclusive=args.exclusive,
        gzip_level=args.gzip_level,
    )
    if args.time:
        stop = time.time()
        print(f"subset index generated in {(stop - start) / 60:.2f} minutes")


def run_adjacency_matrix(args):
    if args.time:
        start = time.time()
    if args.output.endswith(".csv"):
        separator = ","
    elif args.output.endswith(".tsv"):
        separator = "\t"
    else:
        raise RuntimeError("output must end with .csv or .tsv")
    df = get_adjacency_matrix(args.input_dir)
    df.to_csv(args.output, sep=separator)
    if args.time:
        stop = time.time()
        print(f"Matrix generated in {(stop - start) / 60:.2f} minutes")


def run_tree(args):
    if str(args.input).endswith(".csv"):
        adj_matrix = pd.read_csv(args.input, index_col=0)
    elif str(args.input).endswith(".tsv"):
        adj_matrix = pd.read_table(args.input, index_col=0)
    else:
        raise RuntimeError("input must end with .csv or .tsv")
    tree(
        adj_matrix,
        newick=args.newick,
        metric=args.metric,
        method=args.method,
        transformed_matrix=args.transformed_matrix,
    )


def run_clustermap(args):
    if str(args.input).endswith(".csv"):
        adj_matrix = pd.read_csv(args.input, index_col=0)
    elif str(args.input).endswith(".tsv"):
        adj_matrix = pd.read_table(args.input, index_col=0)
    else:
        raise RuntimeError("input must end with .csv or .tsv")
    clustermap(
        adj_matrix,
        args.output,
        cmap=args.colormap,
        width=args.width,
        height=args.height,
        metric=args.metric,
        method=args.method,
        heatmap_tick_pos=args.heatmap_ticks,
        cbar_tick_pos=args.cbar_ticks,
        dendrogram_ratio=args.dend_ratio,
        dendrogram_spacer=args.dend_spacer,
    )


def run_similarity(args):
    if str(args.input).endswith(".csv"):
        adj_matrix = pd.read_csv(args.input, index_col=0)
    elif str(args.input).endswith(".tsv"):
        adj_matrix = pd.read_table(args.input, index_col=0)
    else:
        raise RuntimeError("input must end with .csv or .tsv")
    if args.output.endswith(".csv"):
        separator = ","
    elif args.output.endswith(".tsv"):
        separator = "\t"
    else:
        raise RuntimeError("output must end with .csv or .tsv")
    if args.metric == "jaccard":
        df = adj_to_jaccard(adj_matrix)
    elif args.metric == "overlap":
        df = adj_to_overlap(adj_matrix)
    elif args.metric == "qv":
        df = adj_to_qv(adj_matrix)
    elif args.metric == "qv_symmetric":
        df = adj_to_qv_symmetric(adj_matrix)
    elif args.metric == "ani":
        df = adj_to_ani(adj_matrix)
    else:
        raise RuntimeError("invalid metric")
    df.to_csv(args.output, sep=separator)


def run_distance(args):
    if str(args.input).endswith(".csv"):
        adj_matrix = pd.read_csv(args.input, index_col=0)
    elif str(args.input).endswith(".tsv"):
        adj_matrix = pd.read_table(args.input, index_col=0)
    else:
        raise RuntimeError("input must end with .csv or .tsv")
    if args.output.endswith(".csv"):
        separator = ","
    elif args.output.endswith(".tsv"):
        separator = "\t"
    else:
        raise RuntimeError("output must end with .csv or .tsv")
    if args.metric == "jaccard":
        df = 1 - adj_to_jaccard(adj_matrix)
    elif args.metric == "overlap":
        df = 1 - adj_to_overlap(adj_matrix)
    elif args.metric == "ani":
        df = 1 - adj_to_ani(adj_matrix)
    else:
        raise RuntimeError("invalid metric")
    df.to_csv(args.output, sep=separator)


def run_anchor_region(args):
    if args.output:
        anchor_region(
            *(PKResults(i) for i in args.index),
            anchor=args.anchor,
            coords=args.coords,
            output_file=args.output,
            bgzip=args.bgzip,
            genes=args.genes,
            flank=args.flank,
            threads=args.threads,
        )
    else:
        for chrom, start, end, *values in anchor_region(
            *(PKResults(i) for i in args.index),
            anchor=args.anchor,
            coords=args.coords,
            genes=args.genes,
            flank=args.flank,
            threads=args.threads,
        ):
            print(chrom, start, end, *values, sep="\t")


def run_anchor_genome(args):
    anchor_genome(
        *(PKResults(i) for i in args.index),
        output=args.output,
        anchor=args.anchor,
        chromosomes=args.chromosomes,
        output_table=args.table,
        groups=args.groups,
        title=args.title,
        x_label=args.x_label,
        legend=args.legend,
        legend_title=args.legend_title,
        legend_loc=args.legend_loc,
        bin_size=args.bin_size,
        width=args.width,
        height=args.height,
        color_palette=args.color_palette,
        alpha=args.alpha,
        linewidth=args.linewidth,
        threads=args.threads,
    )


def run_anchor_genome_plot(args):
    plotting_data = pd.read_table(args.table)
    x_label = args.x_label if args.x_label else plotting_data.columns[1]
    legend_title = args.legend_title if args.legend_title else plotting_data.columns[3]
    columns = (
        plotting_data.columns[0],
        x_label,
        plotting_data.columns[2],
        legend_title,
        f"{legend_title}_chrom",
    )
    plotting_data.columns = columns
    if args.chromsizes:
        sizes = pd.read_table(args.chromsizes, header=None)
        sizes.columns = "name", "size"
    else:
        sizes = None
    anchor_genome_plot(
        plotting_data,
        output=args.output,
        groups=args.groups,
        loci=args.loci,
        sizes=sizes,
        title=args.title,
        x_label=x_label,
        legend=args.legend,
        legend_title=legend_title,
        legend_loc=args.legend_loc,
        width=args.width,
        height=args.height,
        color_palette=args.color_palette,
        alpha=args.alpha,
        linewidth=args.linewidth,
    )


def run_anchormap(args):
    anchormap(
        PKResults(args.index),
        args.output,
        args.anchors,
        args.anno,
        threads=args.threads,
    )


def run_anchor_heatmap(args):
    anchor_heatmap(
        PKResults(args.index),
        args.anchors,
        args.features,
        args.output,
        n_features=args.n_features,
        width=args.width,
        height=args.height,
    )


def run_dryrun(args):
    metadata_dict = dryrun(
        genomes_input=args.genomes,
        genomes_input_paired=args.genomes_paired,
        split_memory=args.rounds,
        threads=args.threads,
    )
    json.dump(metadata_dict, sys.stdout)


def run_download_example(args):
    download_example(args.dir, args.clade, args.n_samples)


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    parser.set_defaults(func=lambda _: parser.print_help(sys.stdout))
    subparsers = parser.add_subparsers(dest="func")
    index_parser = subparsers.add_parser("index", help="generate k-mer index")
    index_parser.add_argument(
        "-k",
        "--kmer-size",
        metavar="<int>",
        type=int,
        default=KMER_SIZE,
        help=f"k-mer size, must be an odd integer 8 < k < 32 [{KMER_SIZE}]",
    )
    index_parser.add_argument(
        "-g",
        "--genomes",
        metavar="<genome[s]{.fa,.fq,.tar,/}>",
        nargs="+",
        help="paths to input genomes, directories, or tar archive",
    )
    index_parser.add_argument(
        "-p",
        "--genomes-paired",
        metavar="<genome[s]{.fa,.fq,/}>",
        nargs="+",
        help="paths to input genomes or directories (paired)",
    )
    index_parser.add_argument(
        "-o",
        "--output",
        metavar="<output[.tar]>",
        required=True,
        help="output directory or tarfile that will contain the k-mer index",
    )
    index_parser.add_argument(
        "--rounds",
        metavar="<int>",
        type=int,
        default=1,
        help="split k-mer counting into multiple rounds to reduce memory usage",
    )
    index_parser.add_argument(
        "-t",
        "--threads",
        metavar="<int>",
        type=int,
        help=("Number of threads to use [1]"),
        default=1,
    )
    fraction_group = index_parser.add_mutually_exclusive_group()
    fraction_group.add_argument(
        "--fraction",
        metavar="<float>",
        type=float,
        default=1.0,
        help=("Fraction of k-mers to use. By default all k-mers are kept."),
    )
    fraction_group.add_argument(
        "-q",
        "--qual",
        metavar="<int>",
        type=int,
        help=(
            "Completeness of index, in terms of bases, expressed as a Phred quality score. "
            "e.g. --qual 30 means approx 1 in 1000 bases will be missed, which is "
            "equivalent to --fraction 0.2. By default no bases are missed."
        ),
    )
    index_parser.add_argument(
        "--gzip-level",
        choices=range(1, 10),
        type=int,
        default=6,
        help="gzip compression level [6]",
    )
    index_parser.add_argument(
        "--time", action="store_true", help="Report the time required to execute"
    )
    index_parser.set_defaults(func=run_index_wrapper)

    count_parser = subparsers.add_parser(
        "count", help="count k-mers in one or more indexes"
    )
    count_parser.add_argument(
        "-i",
        "--index",
        metavar="<index[.tar]>",
        type=str,
        action="store",
        dest="index",
        required=True,
        nargs="+",
        help="a k-mer index",
    )
    count_parser.set_defaults(func=run_count)

    collect_parser = subparsers.add_parser(
        "collect", help="calculate k-mer collection curve"
    )
    collect_parser.add_argument(
        "-i",
        "--index",
        metavar="<index[.tar]>",
        type=str,
        action="store",
        required=True,
        help="a k-mer index",
    )
    collect_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.{pdf,png,svg}>",
        type=str,
        action="store",
        dest="output",
        help="destination file for plot",
    )
    collect_parser.add_argument(
        "-t",
        "--table",
        metavar="<output-table.tsv>",
        help="output TSV file containing plotted data",
    )
    collect_parser.add_argument(
        "--title", metavar='<"Plot title">', help="set the title for the plot"
    )
    collect_parser.add_argument(
        "--width",
        metavar="<float>",
        type=float,
        default=4.0,
        help="set width of figure in inches [4]",
    )
    collect_parser.add_argument(
        "--height",
        metavar="<float>",
        type=float,
        default=3.0,
        help="set height of figure in inches [3]",
    )
    collect_parser.add_argument(
        "--color-palette",
        metavar="<#color>",
        nargs="+",
        default=COL_COLOR_PALETTE,
        help="color palette to use",
    )
    collect_parser.add_argument(
        "--alpha",
        metavar="<float>",
        type=float,
        default=1.0,
        help="transparency value for lines [1.0]",
    )
    collect_parser.add_argument(
        "--linewidth",
        metavar="<int>",
        type=int,
        default=3,
        help="line width for plot [3]",
    )
    conf_or_cont = collect_parser.add_mutually_exclusive_group()
    conf_or_cont.add_argument(
        "--conf",
        action="store_true",
        help="calculate confidence intervals for collection curves",
    )
    conf_or_cont.add_argument(
        "--contours",
        metavar="<int>",
        type=int,
        nargs="+",
        help="set contours for collection curves (in percent)",
    )
    collect_parser.add_argument(
        "--legend-loc",
        choices=(
            "best",
            "upper left",
            "upper right",
            "lower left",
            "lower right",
            "outside",
        ),
        default="best",
        help="location of legend [best]",
    )
    collect_parser.set_defaults(func=run_collect)

    upset_parser = subparsers.add_parser("upset", help="generate upset plot")
    upset_parser.add_argument(
        "-i", "--input", metavar="<index[.tar]>", required=True, help="a k-mer index"
    )
    upset_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.{pdf,png,svg}>",
        required=True,
        help="destination file for upset plot",
    )
    upset_parser.add_argument(
        "-g",
        "--genomes",
        metavar="<genome>",
        required=True,
        nargs="+",
        help="list of genomes to include",
    )
    upset_parser.add_argument(
        "-v", "--vertical", action="store_true", help="draw the plot vertically"
    )
    upset_parser.add_argument(
        "-x",
        "--exclusive",
        action="store_true",
        help="exclude k-mers that occur in genomes other than the input set",
    )
    upset_parser.add_argument(
        "-t",
        "--table",
        metavar="<table.tsv[.gz]>",
        help="write (optionally compressed) table of values in tsv format",
    )
    upset_parser.add_argument(
        "--show-counts", action="store_true", help="show counts for each subset"
    )
    upset_parser.add_argument(
        "--min-subset-size",
        metavar="<int>",
        type=int,
        help="show only subsets larger than a minimum size",
    )
    upset_parser.add_argument(
        "--max-subset-size",
        metavar="<int>",
        type=int,
        help="show only subsets smaller than a maximum size",
    )
    upset_parser.add_argument(
        "--time", action="store_true", help="report the time required to execute"
    )
    upset_parser.set_defaults(func=run_upset)

    subset_parser = subparsers.add_parser("subset", help="subset an index")
    subset_parser.add_argument(
        "-i",
        "--input",
        metavar="<input-index[.tar]>",
        required=True,
        help="a k-mer index",
    )
    subset_parser.add_argument(
        "-o",
        "--output",
        metavar="<output-index[.tar]>",
        required=True,
        help="destination file for subset index",
    )
    subset_parser.add_argument(
        "-g",
        "--genomes",
        metavar="<genome>",
        required=True,
        nargs="+",
        help="list of genomes to include ",
    )
    subset_parser.add_argument(
        "-x",
        "--exclusive",
        action="store_true",
        help="exclude k-mers that occur in genomes other than the input set",
    )
    subset_parser.add_argument(
        "--gzip-level",
        choices=range(1, 10),
        type=int,
        default=6,
        help="gzip compression level [6]",
    )
    subset_parser.add_argument(
        "--time", action="store_true", help="report the time required to execute"
    )
    subset_parser.set_defaults(func=run_subset)

    adjmat_parser = subparsers.add_parser(
        "adj-matrix", help="generate adjacency matrix"
    )
    adjmat_parser.add_argument(
        "-i",
        "--input",
        metavar="<index[.tar]>",
        dest="input_dir",
        required=True,
        help="a k-mer index",
    )
    adjmat_parser.add_argument(
        "-o",
        "--output",
        metavar="<adjmatrix.{csv,tsv}>",
        dest="output",
        required=True,
        help="destination file for adjacency matrix",
    )
    adjmat_parser.add_argument(
        "--time", action="store_true", help="Report the time required to execute"
    )
    adjmat_parser.set_defaults(func=run_adjacency_matrix)

    tree_parser = subparsers.add_parser(
        "tree", help="generate a heirarchical clustering tree from an adjacency matrix"
    )
    tree_parser.add_argument(
        "-i",
        "--input",
        metavar="<adjmatrix.{csv,tsv}>",
        dest="input",
        required=True,
        help="adjacency matrix file",
    )
    tree_parser.add_argument(
        "-n",
        "--newick",
        action="store_true",
        dest="newick",
        help="output tree in NEWICK format",
    )
    tree_parser.add_argument(
        "--metric",
        choices=("intersection", "jaccard", "overlap", "qv", "qv_symmetric", "ani"),
        type=str,
        action="store",
        dest="metric",
        default="ani",
        help="similarity metric [intersection]",
    )
    tree_parser.add_argument(
        "--method",
        choices=("single", "complete", "average", "weighted", "centroid"),
        type=str,
        action="store",
        dest="method",
        default="complete",
        help="clustering method [complete]",
    )
    tree_parser.add_argument(
        "--transformed-matrix",
        metavar="<matrix.{csv,tsv}>",
        help="Write similarity transformed matrix to file",
    )
    tree_parser.set_defaults(func=run_tree)

    clustermap_parser = subparsers.add_parser(
        "clustermap", help="plot a clustered heatmap from the adjacency matrix"
    )
    clustermap_parser.add_argument(
        "-i",
        "--input",
        metavar="<adjmatrix.{csv,tsv}>",
        type=str,
        action="store",
        dest="input",
        required=True,
        help="adjacency matrix file",
    )
    clustermap_parser.add_argument(
        "-o",
        "--output",
        metavar="<adjmatrix.{pdf,png,svg}>",
        type=str,
        action="store",
        dest="output",
        required=True,
        help="destination file for plot",
    )
    clustermap_parser.add_argument(
        "--metric",
        choices=("intersection", "jaccard", "overlap", "qv", "qv_symmetric", "ani"),
        type=str,
        action="store",
        dest="metric",
        default="ani",
        help="similarity metric [ani]",
    )
    clustermap_parser.add_argument(
        "--method",
        choices=("single", "complete", "average", "weighted", "centroid"),
        type=str,
        action="store",
        dest="method",
        default="complete",
        help="clustering method [complete]",
    )
    clustermap_parser.add_argument(
        "--colormap",
        metavar="<color_map>",
        type=str,
        action="store",
        default="mako_r",
        help="seaborn colormap for plot [mako_r]",
    )
    clustermap_parser.add_argument(
        "--width",
        metavar="<float>",
        type=float,
        action="store",
        default=7.0,
        help="width of plot in inches [7]",
    )
    clustermap_parser.add_argument(
        "--height",
        metavar="<float>",
        type=float,
        action="store",
        default=7.0,
        help="height of plot in inches [7]",
    )
    clustermap_parser.set_defaults(func=run_clustermap)
    clustermap_parser.add_argument(
        "--heatmap-ticks",
        choices=("left", "right"),
        default="left",
        help='Position of heatmap ticks. Must be "left" or "right" [left]',
    )
    clustermap_parser.add_argument(
        "--cbar-ticks",
        choices=("left", "right"),
        default="left",
        help='Position of color bar ticks. Must be "left" or "right" [left]',
    )
    clustermap_parser.add_argument(
        "--dend-ratio",
        metavar="<float>",
        type=float,
        default=0.2,
        help="Fraction of plot width used for dendrogram [0.2]",
    )
    clustermap_parser.add_argument(
        "--dend-spacer",
        metavar="<float>",
        type=float,
        default=0.1,
        help="Fraction of plot width used as spacer between dendrogram and heatmap [0.1]",
    )
    clustermap_parser.set_defaults(func=run_clustermap)

    similarity_parser = subparsers.add_parser(
        "similarity", help="generate a similarity matrix from an adjacency matrix"
    )
    similarity_parser.add_argument(
        "-i",
        "--input",
        metavar="<adjmatrix.{csv,tsv}>",
        required=True,
        help="adjacency matrix file",
    )
    similarity_parser.add_argument(
        "-o",
        "--output",
        metavar="<simmatrix.{csv,tsv}>",
        required=True,
        help="similarity matrix file",
    )
    similarity_parser.add_argument(
        "--metric",
        choices=("jaccard", "overlap", "qv", "qv_symmetric", "ani"),
        dest="metric",
        default="ani",
        help="similarity metric [jaccard]",
    )
    similarity_parser.set_defaults(func=run_similarity)

    distance_parser = subparsers.add_parser(
        "distance", help="generate a distance matrix from an adjacency matrix"
    )
    distance_parser.add_argument(
        "-i",
        "--input",
        metavar="<adjmatrix.{csv,tsv}>",
        required=True,
        help="adjacency matrix file",
    )
    distance_parser.add_argument(
        "-o",
        "--output",
        metavar="<distmatrix.{csv,tsv}>",
        required=True,
        help="distance matrix file",
    )
    distance_parser.add_argument(
        "--metric",
        choices=("jaccard", "overlap", "ani"),
        dest="metric",
        default="ani",
        help="distance metric [jaccard]",
    )
    distance_parser.set_defaults(func=run_distance)

    anchor_reg_parser = subparsers.add_parser(
        "anchor-region", help="anchor k-mers in a region"
    )
    anchor_reg_parser.add_argument(
        "-i",
        "--index",
        metavar="<index[.tar]>",
        type=str,
        required=True,
        nargs="+",
        help="index",
    )
    anchor_reg_parser.add_argument(
        "-a",
        "--anchor",
        metavar="<anchor.fa.gz>",
        type=str,
        required=True,
        help="anchor genome",
    )
    anchor_reg_parser.add_argument(
        "-c",
        "--coords",
        metavar="<chr:start-end>",
        type=str,
        required=True,
        help="genomic coordinates",
    )
    anchor_reg_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.bdg[.gz]>",
        type=str,
        dest="output",
        help="write to file instead of standard output",
    )
    anchor_reg_parser.add_argument(
        "-b",
        "--bgzip",
        action="store_true",
        dest="bgzip",
        help="block compress the output file",
    )
    anchor_reg_parser.add_argument(
        "-g",
        "--genes",
        metavar="<genes.gff3[.gz]>",
        type=str,
        dest="genes",
        help="gff file of gene coordinates",
    )
    anchor_reg_parser.add_argument(
        "-f",
        "--flank",
        metavar="<int>",
        type=int,
        default=0,
        dest="flank",
        help="size of flanking regions",
    )
    anchor_reg_parser.add_argument(
        "-t",
        "--threads",
        metavar="<int>",
        type=int,
        default=1,
        help="number of threads to use",
    )
    anchor_reg_parser.set_defaults(func=run_anchor_region)

    anchor_genome_parser = subparsers.add_parser(
        "anchor-genome", help="anchor k-mers in a genome"
    )
    anchor_genome_parser.add_argument(
        "-i",
        "--index",
        metavar="<index[.tar]>",
        type=str,
        action="store",
        dest="index",
        required=True,
        nargs="+",
        help="index",
    )
    anchor_genome_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.{pdf,png,svg}>",
        type=str,
        action="store",
        dest="output",
        required=True,
        help="destination file for plot",
    )
    anchor_genome_parser.add_argument(
        "-a",
        "--anchor",
        metavar="<anchor.fa.gz>",
        type=str,
        action="store",
        required=True,
        help="anchor in FASTA format (flat or BGZIP compressed)",
    )
    anchor_genome_parser.add_argument(
        "-c",
        "--chromosomes",
        metavar="<chrX>",
        type=str,
        action="store",
        dest="chromosomes",
        required=True,
        nargs="+",
        help="chromosomes to include",
    )
    anchor_genome_parser.add_argument(
        "--table",
        metavar="<output-table.tsv>",
        help="output TSV file containing plotted data",
    )
    anchor_genome_parser.add_argument(
        "--groups",
        metavar='<"Group">',
        nargs="+",
        help="list of groups for provided indexes [0]",
    )
    anchor_genome_parser.add_argument(
        "--title",
        metavar='<"Plot title">',
        help="set the title for the plot",
    )
    anchor_genome_parser.add_argument(
        "--x-label",
        metavar='<"Label">',
        default="Chromosome",
        help="set the x-axis label for the plot",
    )
    anchor_genome_parser.add_argument(
        "--legend", action="store_true", help="include a legend with the plot"
    )
    anchor_genome_parser.add_argument(
        "--legend-title", metavar='<"Title">', default="Group", help="title of legend"
    )
    anchor_genome_parser.add_argument(
        "--legend-loc",
        choices=(
            "best",
            "upper left",
            "upper right",
            "lower left",
            "lower right",
            "outside",
        ),
        default="best",
        help="location of legend [best]",
    )
    anchor_genome_parser.add_argument(
        "--bin-size",
        metavar="<int>",
        type=int,
        default=0,
        choices=(-2, -1, 0, 1, 2),
        help=(
            "Set bin size. The input <int> is converted to the bin size by "
            "the formula: 10^(<int>+6) bp. The default value is 0, i.e. "
            "1-megabase bins. [0]"
        ),
    )
    anchor_genome_parser.add_argument(
        "--width",
        metavar="<float>",
        type=float,
        default=7.0,
        help="set width of figure in inches [7]",
    )
    anchor_genome_parser.add_argument(
        "--height",
        metavar="<float>",
        type=float,
        default=3.0,
        help="set height of figure in inches [3]",
    )
    anchor_genome_parser.add_argument(
        "--color-palette",
        metavar="<#color>",
        nargs="+",
        default=COLOR_PALETTE,
        help="color palette to use",
    )
    anchor_genome_parser.add_argument(
        "--alpha",
        metavar="<float>",
        type=float,
        default=0.5,
        help="transparency value for lines [0.5]",
    )
    anchor_genome_parser.add_argument(
        "--linewidth",
        metavar="<int>",
        type=int,
        default=3,
        help="line width for plot [3]",
    )
    anchor_genome_parser.add_argument(
        "-t",
        "--threads",
        metavar="<int>",
        type=int,
        default=1,
        help="number of threads to use",
    )
    anchor_genome_parser.set_defaults(func=run_anchor_genome)

    agplot_parser = subparsers.add_parser(
        "anchor-plot", help="generate a plot from genome anchoring results"
    )
    agplot_parser.add_argument(
        "-t",
        "--table",
        metavar="<genomecov.tsv>",
        type=str,
        action="store",
        dest="table",
        required=True,
        help="genomic coverage results",
    )
    agplot_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.{pdf,png,svg}>",
        type=str,
        action="store",
        dest="output",
        required=True,
        help="destination file for plot",
    )
    agplot_parser.add_argument(
        "--groups",
        metavar='<"Group">',
        nargs="+",
        help="list of groups for provided indexes",
    )
    agplot_parser.add_argument(
        "--loci",
        metavar='<"chr:pos:name">',
        nargs="+",
        help="list of loci to mark on plot",
    )
    agplot_parser.add_argument(
        "--chromsizes",
        metavar="<file.chrom.sizes>",
        help="chromsizes file of the anchor used to generate the table",
    )
    agplot_parser.add_argument(
        "--title", metavar='<"Plot title">', help="set the title for the plot"
    )
    agplot_parser.add_argument(
        "--x-label", metavar='<"Label">', help="set x-axis label for the plot"
    )
    agplot_parser.add_argument(
        "--legend", action="store_true", help="include a legend with the plot"
    )
    agplot_parser.add_argument(
        "--legend-title", metavar='<"Title">', help="title of legend"
    )
    agplot_parser.add_argument(
        "--legend-loc",
        choices=(
            "best",
            "upper left",
            "upper right",
            "lower left",
            "lower right",
            "outside",
        ),
        default="best",
        help="location of legend [best]",
    )
    agplot_parser.add_argument(
        "--width",
        metavar="<float>",
        type=float,
        default=7.0,
        help="set width of figure in inches [7]",
    )
    agplot_parser.add_argument(
        "--height",
        metavar="<float>",
        type=float,
        default=3.0,
        help="set height of figure in inches [3]",
    )
    agplot_parser.add_argument(
        "--color-palette",
        metavar="<#color>",
        nargs="+",
        default=COLOR_PALETTE,
        help="color palette to use",
    )
    agplot_parser.add_argument(
        "--alpha",
        metavar="<float>",
        type=float,
        default=0.5,
        help="transparency value for lines [0.5]",
    )
    agplot_parser.add_argument(
        "--linewidth",
        metavar="<int>",
        type=int,
        default=3,
        help="line width for plot [3]",
    )
    agplot_parser.set_defaults(func=run_anchor_genome_plot)

    anchor_hm_parser = subparsers.add_parser(
        "anchor-heatmap", help="draw anchor heatmap"
    )
    anchor_hm_parser.add_argument(
        "-i",
        "--index",
        metavar="<index[.tar]>",
        type=str,
        action="store",
        dest="index",
        required=True,
        help="index",
    )
    anchor_hm_parser.add_argument(
        "-a",
        "--anchors",
        metavar="<anchors.fa.gz>",
        type=str,
        action="store",
        required=True,
        nargs="+",
        help="anchors",
    )
    anchor_hm_parser.add_argument(
        "-f",
        "--features",
        metavar="<features.gff3>",
        type=str,
        action="store",
        dest="features",
        required=True,
        nargs="+",
        help="GFF files defining features (such as genes)",
    )
    anchor_hm_parser.add_argument(
        "-o",
        "--output",
        metavar="<output.{pdf,png,svg}>",
        type=str,
        action="store",
        dest="output",
        required=True,
        help='output file (must end with ".png")',
    )
    anchor_hm_parser.add_argument(
        "--n-features",
        metavar="<int>",
        type=int,
        action="store",
        dest="n_features",
        help="use to limit plotting to the first n features for each genome",
    )
    anchor_hm_parser.add_argument(
        "--width",
        metavar="<float>",
        type=float,
        action="store",
        dest="width",
        default=7,
        help="width of plot in inches",
    )
    anchor_hm_parser.add_argument(
        "--height",
        metavar="<float>",
        type=float,
        action="store",
        dest="height",
        default=7,
        help="height of plot in inches",
    )
    anchor_hm_parser.set_defaults(func=run_anchor_heatmap)

    anchormap_parser = subparsers.add_parser(
        "anchormap", help="export an anchormap for downstream visualization"
    )
    anchormap_parser.add_argument(
        "-i", "--index", metavar="<index[.tar]>", required=True, help="index"
    )
    anchormap_parser.add_argument(
        "-o",
        "--output",
        metavar="<anchormap_dir/>",
        required=True,
        help="output directory for the anchormap",
    )
    anchormap_parser.add_argument(
        "--anchors",
        metavar="<anchor.fasta[.gz]>",
        required=True,
        nargs="+",
        help="the anchor genomes",
    )
    anchormap_parser.add_argument(
        "--anno",
        metavar="<anno.gff[.gz]>",
        required=True,
        nargs="+",
        help="annotations",
    )
    anchormap_parser.add_argument(
        "-t",
        "--threads",
        metavar="<int>",
        type=int,
        help="Number of threads to use",
        default=1,
    )
    anchormap_parser.set_defaults(func=run_anchormap)

    dryrun_parser = subparsers.add_parser(
        "dryrun", help="perform a dry run of indexing and print metadata"
    )
    dryrun_parser.add_argument(
        "-g",
        "--genomes",
        metavar="<genome[s]{.fa,.fq,.tar,/}>",
        nargs="+",
        help="input genomes",
    )
    dryrun_parser.add_argument(
        "-p",
        "--genomes-paired",
        metavar="<genome[s]{.fa,.fq,/}>",
        nargs="+",
        help="input genomes (paired)",
    )
    dryrun_parser.add_argument(
        "--rounds",
        metavar="<int>",
        type=int,
        help=(
            "Parallel."
            "This splits k-mer counting into multiple rounds, reducing memory usage."
        ),
        default=1,
    )
    dryrun_parser.add_argument(
        "-t",
        "--threads",
        metavar="<int>",
        type=int,
        help=("Number of threads to use"),
        default=1,
    )
    dryrun_parser.set_defaults(func=run_dryrun)

    download_parser = subparsers.add_parser(
        "download-example",
        help="Download an example dataset. A. thaliana pseudo-genomes "
        "from 1001 Genomes . These sequence data were "
        "produced by the Weigel laboratory at the Max Planck Institute "
        "for Developmental Biology.",
    )
    download_parser.add_argument(
        "-d",
        "--dir",
        metavar="<dir/>",
        type=str,
        action="store",
        dest="dir",
        default=EXAMPLE_DATA_DIR,
        help="destination directory for example data",
    )
    download_parser.add_argument(
        "-c",
        "--clade",
        choices=("Spolyrhiza", "Solanum", "Zea", "Hsapiens", "Bsubtilis", "Athaliana"),
        help=(
            "download publicly available genomes. Clade: max_samples. "
            "Spolyrhiza: 3, Solanum: 46, Zea: 54, Hsapiens: 94, Bsubtilis: 164, Athaliana: 1135"
        ),
    )
    download_parser.add_argument(
        "-n",
        "--n-samples",
        metavar="<int>",
        type=int,
        default=1,
        action="store",
        dest="n_samples",
        help="number of samples to download, must be less than clade max [1]",
    )
    download_parser.set_defaults(func=run_download_example)

    args = parser.parse_args()
    args.func(args)


# def update_index(upper, lower, kmer_bitsize, score_bitsize, genomes, outdir, index_dir):
#     gnum = len(genomes)
#     kmers_post = {}
#     kmers = get_kmers(upper, lower, genomes)
#     print_err(f"Saving {lower}-{upper} kmers.")
#     kmers_out_path = join(outdir, f'kmers_{lower}_{upper}.b.gz')
#     scores_out_path = join(outdir, f'scores_{lower}_{upper}.b.gz')
#     kmers_exist = sorted(kmers.keys())
#     results = PKResults(index_dir)
#     total_genomes_number = score_bitsize + results.number_of_genomes
#     new_score_bitsize = math.ceil(total_genomes_number/8)
#     # Find lower bound position from index
#     initial_lower_bound = get_lower_bound(results.positions, lower)
#     # Move iterator from initial lower bound to actual lower bound
#     if initial_lower_bound != None:
#         results.seek_kmer(initial_lower_bound)
#         results.seek_score(initial_lower_bound)
#     lb_bit = int(lower).to_bytes(results.kmer_bitsize, byteorder="big", signed=False) # lower bound bit
#     ub_bit = int(upper).to_bytes(results.kmer_bitsize, byteorder="big", signed=False) # upper bound bit
#     results_iter = iter(results)
#     try:
#         index_kmer, index_score = next(results_iter)
#     except StopIteration:
#         index_kmer, index_score = [None, None]
#     while index_kmer != None and index_kmer < lb_bit:
#         try:
#             index_kmer, index_score = next(results_iter)
#         except StopIteration:
#             index_kmer, index_score = [None, None]
#     dict_iter = iter(kmers_exist)
#     if kmers_exist:
#         dict_kmer = next(dict_iter)
#         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                         byteorder="big", signed=False)
#     else:
#         dict_kmer = None
#     count = 0
#     kmer_to_write = None
#     score_to_write = None
#     with gzip.open(kmers_out_path, 'wb') as kmers_out, gzip.open(scores_out_path,'wb') as scores_out:
#         with io.BufferedWriter(scores_out, buffer_size=1000*score_bitsize) as so_buffer ,\
#             io.BufferedWriter(kmers_out, buffer_size=1000*kmer_bitsize) as ko_buffer:
#             while (index_kmer != None and index_kmer <= ub_bit) or dict_kmer != None:
#                 if count%10000000 == 0 and count != 0:
#                     kmers_post[kmer_to_write] = count
#                     count = 0
#                 # Current samples don't have any Kmers left
#                 # but pre-existing index still has Kmers
#                 if dict_kmer == None and index_kmer != None:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     index_kmer_int = int.from_bytes(index_kmer, 'big', signed=False)
#                     kmer_to_write = index_kmer_int
#                     score_to_write = score << gnum
#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Current samples have Kmers left
#                 # but pre-existing index doesn't have any Kmers left
#                 elif dict_kmer != None and index_kmer == None:
#                     kmer_to_write = dict_kmer
#                     score_to_write = kmers[dict_kmer]
#                     try:
#                         dict_kmer = next(dict_iter)
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                         byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None
#                 # Current sample Kmer and pre-existing Kmer is the same
#                 elif index_kmer == dict_kmer_bit:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     new_score = (score << gnum) | kmers[dict_kmer]
#                     # kmers[dict_kmer_bit] = new_score
#                     kmer_to_write = dict_kmer
#                     score_to_write = new_score
#                     try:
#                         dict_kmer = next(dict_iter)
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                     byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None

#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Add pre-existing Kmer
#                 elif index_kmer < dict_kmer_bit or dict_kmer == None:
#                     score = int.from_bytes(index_score, 'big', signed=False)
#                     index_kmer_int = int.from_bytes(index_kmer, 'big', signed=False)
#                     new_score = score << gnum
#                     # kmers[index_kmer] = new_score
#                     kmer_to_write = index_kmer_int
#                     score_to_write = new_score

#                     try:
#                         index_kmer, index_score = next(results_iter)
#                     except StopIteration:
#                         index_kmer, index_score = [None, None]
#                 # Add current sample Kmer
#                 else:
#                     kmer_to_write = dict_kmer
#                     score_to_write = kmers[dict_kmer]
#                     try:
#                         dict_kmer = next(dict_iter)
#                         dict_kmer_bit = dict_kmer.to_bytes(results.kmer_bitsize,
#                                                         byteorder="big", signed=False)
#                     except StopIteration:
#                         dict_kmer = None
#                 a = ko_buffer.write(
#                     kmer_to_write.to_bytes(kmer_bitsize,
#                     byteorder="big", signed=False))
#                 b = so_buffer.write(
#                     score_to_write.to_bytes(new_score_bitsize,
#                     byteorder="big", signed=False))
#                 count += 1
#             if kmer_to_write != None and kmer_to_write not in kmers_post:
#                 kmers_post[kmer_to_write] = count-1
#     return kmers_post