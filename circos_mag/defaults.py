import os

SRC_DIR = os.path.dirname(__file__)

CIRCOS_CONFIG_FILE_DIR = os.path.join(SRC_DIR, '..', 'config_files')

MIN_CONTIG_LEN = 1
MAX_CONTIGS = 10_000

GC_WINDOW_SIZE = 1000
COV_WINDOW_SIZE = 1000

# minimum length for tick marks to be drawn on a contig
MIN_CONTIG_LEN_FOR_TICKS = 5_000

# annotation(s) used for hypothetical proteins
HYPOTHETICAL_PROTEINS = set(['hypothetical protein'])
