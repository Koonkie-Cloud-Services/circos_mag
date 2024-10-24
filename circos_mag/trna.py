"""
Create Circos file indicate position of tRNA genes.
"""

import os
import logging
from collections import defaultdict


class tRNA():
    """Create Circos file indicate position of tRNA genes."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               gff_file: str,
               output_dir: str) -> str:
        """Create Circos file indicate position of tRNA genes."""

        # create tract indicating deviation from mean GC
        trna_counts = defaultdict(int)
        trna_file = os.path.join(output_dir, 'trna.tsv')
        fout = open(trna_file, 'w')
        with open(gff_file) as f:
            for line in f:
                if line.startswith('##FASTA'):
                    # GFF files can end with the full genomic
                    # FASTA file of the genome
                    break

                if line[0] == '#':
                    # skip comment lines
                    continue

                tokens = line.strip().split('\t')
                feature_type = tokens[2]
                if feature_type != 'tRNA':
                    continue

                contig_id = tokens[0]
                start_pos = tokens[3]
                end_pos = tokens[4]

                additional_info_tokens = tokens[-1].split(';')
                for info_token in additional_info_tokens:
                    if info_token.startswith('product='):
                        product = info_token.split('=')[-1]
                        trna_counts[product] += 1

                fout.write(f'{contig_id} {start_pos} {end_pos} A\n')

        fout.close()

        return trna_counts
