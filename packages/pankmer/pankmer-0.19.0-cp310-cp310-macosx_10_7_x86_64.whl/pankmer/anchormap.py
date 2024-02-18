from Bio.bgzf import BgzfWriter
import gff2bed
import json
import math
import os.path
import os
import pybedtools
import pysam
import subprocess

from pankmer.tree import adj_to_jaccard
from pankmer.adjacency_matrix import get_adjacency_matrix
from pankmer.anchor import check_for_bgzip, get_chromosome_sizes_from_anchor

LOWRES_STEP = 100


def anchormap(pk_results, output_dir, anchors, anno, threads: int = 1):
    """Generate an anchormap for visualization

    Parameters
    ----------
    pk_results : PKResults
        a PKResults object
    output_dir
        directory for output files
    anchors
        iterable of paths to anchor genomes
    anno
        iterable of paths to annotation files
    threads : int
        number of threads to use
    """
    for anchor in anchors:
        check_for_bgzip(anchor)
    os.mkdir(output_dir)
    os.mkdir(os.path.join(output_dir, "anchors"))
    os.mkdir(os.path.join(output_dir, "anno"))
    print("loading index")
    pk_results.threads = threads
    print("writing distance matrix")
    (1 - adj_to_jaccard(get_adjacency_matrix(pk_results))).to_csv(
        os.path.join(output_dir, 'distance.tsv'), sep='\t')
    score_bitsize = math.ceil(pk_results.number_of_genomes/8)
    print('writing config')
    sizes = {'.'.join(os.path.basename(a).split('.')[:-2]):
             get_chromosome_sizes_from_anchor(a).set_index('name')['size']
             for a in anchors}
    with open(os.path.join(output_dir,'config.json'), 'w') as f:
        json.dump({
            'prefix': output_dir,
            'genomes': list(pk_results.genomes),
            'anchors': ['.'.join(os.path.basename(a).split('.')[:-2])
                        for a in anchors],
            'lowres_step': LOWRES_STEP,
            'sizes': {a: [[chrom, size] for chrom, size in zip(s.index, s)]
                      for a, s in sizes.items()}},
            f)
    for anchor, anno in zip(anchors, anno):
        print("collecting regional scores")
        a = ".".join(os.path.basename(anchor).split(".")[:-2])
        regcov_dict = pk_results.get_collapsed_regional_scores(
            anchor, {c: [[1, sizes[a][c]]] for c in sizes[a].index}
        )
        print("converting to bytes")
        scores = b"".join(
            int("".join(str(i) for i in s), 2).to_bytes(
                score_bitsize, byteorder="big", signed=False
            )
            for c in sizes[a].index
            for s in regcov_dict[c][(1, sizes[a][c])]
        )
        print("writing scoremap")
        for step in 1, LOWRES_STEP:
            with BgzfWriter(
                os.path.join(output_dir, "anchors", f"{a}.{step}.bgz"), "wb"
            ) as scores_out:
                scores_out.write(scores[::step] if step > 1 else scores)
            subprocess.run(
                (
                    "bgzip",
                    "-rI",
                    os.path.join(output_dir, "anchors", f"{a}.{step}.gzi"),
                    os.path.join(output_dir, "anchors", f"{a}.{step}.bgz"),
                )
            )
        print("formatting annotations")
        for type in "gene", "anno":
            bed = os.path.join(output_dir, "anno", f"{a}.{type}.bed")
            tbx = os.path.join(output_dir, "anno", f"{a}.{type}.bed.bgz")
            pybedtools.BedTool(gff2bed.convert(gff2bed.parse(anno))).saveas(
                bed
            ).sort().saveas(bed)
            pysam.tabix_compress(bed, tbx, True)
            pysam.tabix_index(tbx, True, 0, 1, 2, csi=True)
