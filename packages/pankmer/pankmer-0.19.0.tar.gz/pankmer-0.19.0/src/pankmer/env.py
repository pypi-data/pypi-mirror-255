import re
import os
import os.path

COORD_REGEX = re.compile(
    os.environ.get(
        "PANKMER_COORD_REGEX",  # Not used yet, but will be useful later
        "[\s\S]+:[0-9]+-[0-9]+$",
    )
)
# '([Cc]hr)?[0-9XY]+:[0-9]+-[0-9]+$'))
GENES_PATH = os.environ.get(
    "PANKMER_GENES_PATH"
)  # Not used yet, but will be useful later

EXAMPLE_DATA_URL = "https://salk-tm-pub.s3.us-west-2.amazonaws.com/PanKmer_example/PanKmer_example_Sp_Chr19.tar.gz"
EXAMPLE_DATA_DIR = os.environ.get("PANKMER_EXAMPLE_DATA_DIR", os.path.dirname(__file__))
KMER_SIZE = os.environ.get("PANKMER_KMER_SIZE", 31)
