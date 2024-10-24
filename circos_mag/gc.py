"""
Create Circos file indicate GC content across contigs.
"""

import os
import logging

import seq_io as seq_io
import seq_tk as seq_tk


class GC():
    """Create Circos file indicate GC content across contigs."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               genome_file: str,
               window_size: int,
               output_dir: str) -> str:
        """Create Circos file indicate GC content across contigs."""

        # calculate mean GC
        gc = 0
        total_bases = 0
        for _contig_id, contig in seq_io.read_seq(genome_file):
            a, c, g, t = seq_tk.count_nt(contig)
            gc += g + c
            total_bases += a + c + g + t

        mean_gc = 100.0 * gc / total_bases

        # create tract indicating deviation from mean GC
        gc_file = os.path.join(output_dir, 'gc.tsv')
        fout = open(gc_file, 'w')
        for contig_id, contig in seq_io.read_seq(genome_file):
            for start_idx in range(0, len(contig), window_size):
                end_idx = start_idx + window_size
                if end_idx >= len(contig):
                    # ensure last window is still calculate over the
                    # same number of bases to avoid spurious spikes
                    end_idx = len(contig)-1
                    start_idx = len(contig)-window_size

                gc_window = seq_tk.gc(contig[start_idx:end_idx])
                delta_gc = 100*gc_window - mean_gc

                color = 'dorange'
                if delta_gc < 0:
                    color = 'dblue'

                fout.write(f'{contig_id} {start_idx} {end_idx} {delta_gc} fill_color={color}\n')

        fout.close()

        return mean_gc
