"""
Create Circos file indicate position of 5S/16S/23S rRNA genes.
"""

import os
import logging
from collections import defaultdict

from circos_mag.plot_style import PlotStyle


class rRNA():
    """Create Circos file indicate position of 5S/16S/23S rRNA genes."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               gff_file: str,
               plot_style: PlotStyle,
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

                if product:
                    rrna_counts[product] += 1

                if product is None:
                    self.logger.warning('No rRNA product in GFF file:')
                    self.logger.warning(f'{line.strip()}')
                elif product.startswith('5S'):
                    symbol = plot_style.rrna_5S_symbol
                    color = plot_style.rrna_5S_symbol_color
                elif product.startswith('16S'):
                    symbol = plot_style.rrna_16S_symbol
                    color = plot_style.rrna_16S_symbol_color
                elif product.startswith('23S'):
                    symbol = plot_style.rrna_23S_symbol
                    color = plot_style.rrna_23S_symbol_color
                else:
                    self.logger.warning(f'Unknown rRNA product in GFF file: {product}')
                    continue

                row = f'{contig_id} {start_pos} {end_pos}'
                row += f' {symbol} color={color}'

                fout.write(f'{row}\n')

        fout.close()

        return rrna_counts
