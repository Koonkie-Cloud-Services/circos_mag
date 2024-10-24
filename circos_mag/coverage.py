"""
Create Circos file indicate coverage across contigs.
"""

import os
import logging
import gzip
from typing import Tuple, Dict
from collections import defaultdict

import seq_io as seq_io
import seq_tk as seq_tk


class Coverage():
    """Create Circos file indicate coverage across contigs."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               genome_file: str,
               coverage_file: str,
               window_size: int,
               output_dir: str) -> Tuple[float, Dict[str, float]]:
        """Create Circos file indicate coverage across contigs."""

        # get contigs in genome
        contigs = {}
        for contig_id, contig in seq_io.read_seq(genome_file):
            contigs[contig_id] = len(contig)

        # determine coverage across windows
        contig_window_coverage = defaultdict(lambda: defaultdict(int))
        total_bases = 0
        total_cov = 0

        open_file = open
        if coverage_file.endswith('.gz'):
            open_file = gzip.open

        with open_file(coverage_file, 'rt') as f:
            for line in f:
                tokens = line.strip().split('\t')

                contig_id = tokens[0]
                if contig_id not in contigs:
                    continue

                base_idx = int(tokens[1])
                base_cov = int(tokens[2])

                window_idx = int(base_idx / window_size)
                contig_window_coverage[contig_id][window_idx] += base_cov

                total_bases += 1
                total_cov += base_cov

        mean_cov = total_cov / total_bases

        # create tract indicating deviation from mean GC
        cov_file = os.path.join(output_dir, 'coverage.tsv')
        fout = open(cov_file, 'w')
        for contig_id in contig_window_coverage:
            for window_idx, window_base_count in contig_window_coverage[contig_id].items():
                window_cov = window_base_count / window_size

                start_idx = window_idx*window_size
                end_idx = (window_idx+1)*window_size
                if end_idx >= contigs[contig_id]:
                    end_idx = contigs[contig_id]-1
                    if end_idx == start_idx:
                        # no need to plot this point
                        continue
                    window_cov = window_base_count / (end_idx - start_idx)

                cov_perc_diff = 100.0 * (window_cov - mean_cov) / mean_cov

                color = 'dorange'
                if cov_perc_diff < 0:
                    color = 'dblue'

                fout.write(f'{contig_id} {start_idx} {end_idx} {cov_perc_diff} fill_color={color}\n')

        fout.close()

        # calculate coverage for each contig
        contig_cov = {}
        for contig_id in contig_window_coverage:
            total_base_cov = sum([v for v in contig_window_coverage[contig_id].values()])
            contig_cov[contig_id] = total_base_cov / contigs[contig_id]

        return mean_cov, contig_cov
