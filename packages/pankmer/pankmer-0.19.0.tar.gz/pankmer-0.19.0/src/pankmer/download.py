import urllib3
import shutil
import os
import os.path
import tarfile
import ftplib
import tempfile
import subprocess
from pankmer.env import EXAMPLE_DATA_URL, EXAMPLE_DATA_DIR
from pankmer.datasets import (
    SPOLYRHIZA_URL,
    SPOLYRHIZA_FILES,
    SOLANUM_URL_FORMAT,
    SOLANUM_IDS,
    ZEA_URL,
    ZEA_FILES,
    HSAPIENS_URL,
    HSAPIENS_AGC,
    HSAPIENS_AGC_BINARY_URL,
    HSAPIENS_IDS,
    ATHALIANA_URL_FORMAT,
    ATHALIANA_IDS,
    BSUBTILIS_DATA_FTP,
    BSUBTILIS_DATA_PATHS,
)


def download_example(dir: str = EXAMPLE_DATA_DIR, clade=None, n_samples: int = 1):
    """Download an example datatset. A. thaliana pseudo-genomes from 1001
    Genomes. These sequence data were produced by the Weigel laboratory at the
    Max Planck Institute for Developmental Biology.

    Parameters
    ----------
    dir : str
        Destination directory for example data
    clade
        If None, download small example dataset. if str, download publicly
        available genomes. Clade: max_samples. Spolyrhiza: 3, Bsubtilis: 164,
        Solanum: 46, Zea: 54, Hsapiens: 94, Athaliana: 1135
    n_samples : int
        Number of samples to download, must be less than max [1]
    """

    if clade == "Spolyrhiza":
        if n_samples > 3:
            raise RuntimeError("n_samples parameter must be <= 3 for Spolyrhiza")
        http = urllib3.PoolManager()
        with tempfile.TemporaryDirectory(dir=dir) as temp_dir:
            tar_file_path = os.path.join(temp_dir, os.path.basename(SPOLYRHIZA_URL))
            if os.path.exists(tar_file_path[:-7]):
                raise RuntimeError("destination already exists")
            with http.request("GET", SPOLYRHIZA_URL, preload_content=False) as r, open(
                tar_file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)
            with tarfile.open(tar_file_path) as tar:
                tar.extractall(temp_dir)
            os.remove(tar_file_path)
            for fasta_file in SPOLYRHIZA_FILES[:n_samples]:
                shutil.move(
                    os.path.join(temp_dir, "Spolyrhiza_genomes", fasta_file),
                    os.path.join(dir, fasta_file),
                )
            shutil.rmtree(os.path.join(temp_dir, "Spolyrhiza_genomes"))

    elif clade == "Solanum":
        if n_samples > 46:
            raise RuntimeError("n_samples parameter must be <= 46 for Solanum")
        http = urllib3.PoolManager()
        for genome_id in SOLANUM_IDS[:n_samples]:
            fasta_url = SOLANUM_URL_FORMAT.format(genome_id)
            dest_file_path = os.path.join(dir, os.path.basename(fasta_url))
            if os.path.exists(dest_file_path):
                raise RuntimeError("destination already exists")
            with http.request("GET", fasta_url, preload_content=False) as r, open(
                dest_file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)

    elif clade == "Zea":
        if n_samples > 54:
            raise RuntimeError("n_samples parameter must be <= 54 for Zea")
        http = urllib3.PoolManager()
        for fasta_file in ZEA_FILES[:n_samples]:
            fasta_url = os.path.join(ZEA_URL, fasta_file)
            dest_file_path = os.path.join(dir, os.path.basename(fasta_url))
            if os.path.exists(dest_file_path):
                raise RuntimeError("destination already exists")
            with http.request("GET", fasta_url, preload_content=False) as r, open(
                dest_file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)

    elif clade == "Hsapiens":
        if n_samples > 94:
            raise RuntimeError("n_samples parameter must be <= 94 for Hsapiens")
        http = urllib3.PoolManager()
        with tempfile.TemporaryDirectory(dir=dir) as temp_dir:
            tar_file_path = os.path.join(
                temp_dir, os.path.basename(HSAPIENS_AGC_BINARY_URL)
            )
            agc_binary_path = os.path.join(temp_dir, "agc-1.1_x64-linux", "agc")
            agc_file_path = os.path.join(temp_dir, HSAPIENS_AGC)
            with http.request(
                "GET", HSAPIENS_AGC_BINARY_URL, preload_content=False
            ) as r, open(tar_file_path, "wb") as out_file:
                shutil.copyfileobj(r, out_file)
            with tarfile.open(tar_file_path) as tar:
                tar.extractall(temp_dir)
            with http.request("GET", HSAPIENS_URL, preload_content=False) as r, open(
                agc_file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)
            for genome_id in HSAPIENS_IDS[:n_samples]:
                with open(os.path.join(dir, f"{genome_id}.fa"), "wb") as f:
                    subprocess.run(
                        (agc_binary_path, "getset", agc_file_path, genome_id), stdout=f
                    )

    elif clade == "Bsubtilis":
        if n_samples > 164:
            raise RuntimeError("n_samples parameter must be <= 164 for Bsubtillis")
        ftp = ftplib.FTP(BSUBTILIS_DATA_FTP)
        ftp.login()
        for ftp_path in BSUBTILIS_DATA_PATHS[:n_samples]:
            with open(os.path.join(dir, os.path.basename(ftp_path)), "wb") as f:
                ftp.retrbinary(f"RETR {ftp_path}", f.write)

    elif clade == "Athaliana":
        if n_samples > 1135:
            raise RuntimeError("n_samples parameter must be <= 1135 for Athaliana")
        http = urllib3.PoolManager()
        for pseudo in ATHALIANA_IDS[:n_samples]:
            fasta_url = ATHALIANA_URL_FORMAT.format(pseudo)
            dest_file_path = os.path.join(dir, os.path.basename(fasta_url))
            if os.path.exists(dest_file_path):
                raise RuntimeError("destination already exists")
            with http.request("GET", fasta_url, preload_content=False) as r, open(
                dest_file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)

    elif isinstance(clade, str):
        raise RuntimeError("invalid clade")

    else:
        http = urllib3.PoolManager()
        tar_file_path = os.path.join(dir, os.path.basename(EXAMPLE_DATA_URL))
        if os.path.exists(tar_file_path[:-7]):
            raise RuntimeError("destination already exists")
        with http.request("GET", EXAMPLE_DATA_URL, preload_content=False) as r, open(
            tar_file_path, "wb"
        ) as out_file:
            shutil.copyfileobj(r, out_file)
        with tarfile.open(tar_file_path) as tar:
            tar.extractall(dir)
        os.remove(tar_file_path)
