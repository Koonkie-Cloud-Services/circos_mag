"""
Create Circos file indicate position of 5S/16S/23S rRNA genes.
"""

import os
import logging
from collections import defaultdict


class rRNA():
    """Create Circos file indicate position of 5S/16S/23S rRNA genes."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               gff_file: str,
               output_dir: str) -> str:
        """Create Circos file indicate position of 5S/16S/23S rRNA genes."""

        # create tract indicating deviation from mean GC
        rrna_counts = defaultdict(int)
        trna_file = os.path.join(output_dir, 'rrna.tsv')
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
                if feature_type != 'rRNA':
                    continue

                contig_id = tokens[0]
                start_pos = tokens[3]
                end_pos = tokens[4]

                product = None
                additional_info_tokens = tokens[-1].split(';')
                for info_token in additional_info_tokens:
                    if info_token.startswith('product='):
                        product = info_token.split('=')[-1]

                rrna_type = None
                if product is None:
                    self.logger.warning('No rRNA product in GFF file:')
                    self.logger.warning(f'{line.strip()}')
                elif product.startswith('5S'):
                    rrna_type = '5S'
                elif product.startswith('16S'):
                    rrna_type = '16S'
                elif product.startswith('23S'):
                    rrna_type = '23S'
                else:
                    self.logger.warning(f'Unknown rRNA product in GFF file: {product}')

                if product:
                    rrna_counts[product] += 1

                if rrna_type:
                    fout.write(f'{contig_id} {start_pos} {end_pos} {rrna_type}\n')

        fout.close()

        return rrna_counts
