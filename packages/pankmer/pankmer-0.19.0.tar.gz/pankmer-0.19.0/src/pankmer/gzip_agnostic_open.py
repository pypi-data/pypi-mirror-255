import gzip
from io import BytesIO, TextIOWrapper


def nothing(x):
    return x


def gzip_agnostic_open(file_path, mode="rb", tar=None, **kwargs):
    """
    Open a file (e.g. FASTA) which may or may not be inside a tar file and
    may or may not be gzipped

    Parameters
    ----------
    file_path
        path to file, possibly relative to tar file
    mode
        file open mode, should be 'rb' or 'rt' [rb]
    tar
        tar file object containing file_path, or None
    **kwargs
        other arguments passed to open() or BytesIO()
    """

    return (
        gzip.open(
            tar.extractfile(file_path) if tar is not None else file_path, mode, **kwargs
        )
        if str(file_path).endswith(".gz")
        else (
            (lambda b: TextIOWrapper(b) if mode[1] == "t" else b)(
                BytesIO(tar.extractfile(file_path).read()), **kwargs
            )
            if tar is not None
            else open(file_path, mode, **kwargs)
        )
    )
