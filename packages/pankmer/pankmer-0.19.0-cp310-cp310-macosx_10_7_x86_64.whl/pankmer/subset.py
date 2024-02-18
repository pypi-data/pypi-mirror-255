from os.path import isfile
import shutil
import tarfile
from pankmer.index import subset as _subset
from pankmer.version import __version__


def subset(index, output, genomes, exclusive=False, gzip_level=6):
    output_is_tar = output.endswith(".tar")
    output_dir = output[:-4] if output_is_tar else output
    _subset(
        str(index),
        str(index) if isfile(index) and tarfile.is_tarfile(index) else "",
        genomes,
        output_dir,
        gzip_level,
        exclusive,
    )
    if output_is_tar:
        with tarfile.open(output, "w") as tar:
            tar.add(output_dir)
        shutil.rmtree(output_dir)
