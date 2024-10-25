"""
Create a Circos karyotype file for a MAG.
"""

import os
import logging
from dataclasses import dataclass

import circos_mag.seq_tk as seq_tk
import circos_mag.defaults as Defaults


@dataclass
class GenomeStats:
    num_contigs: int
    n50_contigs: int
    l50_contigs: int
    genome_size: int
    missing_size: int
    num_cds: int
    num_annotated_proteins: int
    num_hypothetical_proteins: int


class Karyotype():
    """Create a Circos karyotype file for a MAG."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def create(self,
               genome_file: str,
               gff_file: str,
               completeness: float,
               min_contig_len: int,
               max_contigs: int,
               output_dir: str) -> GenomeStats:
        """Create a Circos karyotype file for a MAG."""

        # read contigs
        contigs = {}
        for contig_id, contig in seq_tk.read_seq(genome_file):
            contigs[contig_id] = contig

        # get length of contigs and genome
        contig_lens = seq_tk.contig_lengths(contigs)

        genome_size = sum([v for v in contig_lens.values()])
        missing_size = int(genome_size/(completeness/100.0) - genome_size)

        # sort contigs from largest to smallest
        sorted_contigs = {}
        for contig_id, contig_len in sorted(contig_lens.items(), key=lambda kv: kv[1], reverse=True):
            sorted_contigs[contig_id] = contig_len

        # create Karyotype file
        karyotype_file = os.path.join(output_dir, 'karyotype.tsv')
        fout = open(karyotype_file, 'w')
        other_contig_bps = 0
        for idx, (contig_id, contig_len) in enumerate(sorted_contigs.items()):
            if contig_len < min_contig_len or idx == max_contigs:
                other_contig_bps += contig_len

            fout.write(f'chr - {contig_id} {idx+1} 0 {contig_len} lgreen\n')

        # draw extra chromosome representing any skipped contigs
        if other_contig_bps > 0:
            fout.write(f'chr - other {len(contig_lens)+1} 0 {missing_size} grey\n')

        # draw extra chromosome representing missing DNA
        if missing_size > 0:
            fout.write(f'chr - missing_dna {len(contig_lens)+1} 0 {missing_size} dred\n')

        fout.close()

        # get number of CDS with and without annotation
        num_hypothetical_proteins = 0
        num_annotated_proteins = 0
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
                if feature_type != 'CDS':
                    continue

                product = None
                additional_info_tokens = tokens[-1].split(';')
                for info_token in additional_info_tokens:
                    if info_token.startswith('product='):
                        product = info_token.split('=')[-1]

                if product is None:
                    self.logger.warning('No CDS product in GFF file:')
                    self.logger.warning(f'{line.strip()}')
                elif product in Defaults.HYPOTHETICAL_PROTEINS:
                    num_hypothetical_proteins += 1
                else:
                    num_annotated_proteins += 1

        # save genome stats
        n50, l50 = seq_tk.N50_L50(contigs)
        genome_stats = GenomeStats(
            num_contigs=len(contigs),
            n50_contigs=n50,
            l50_contigs=l50,
            genome_size=genome_size,
            missing_size=missing_size,
            num_cds=num_annotated_proteins + num_hypothetical_proteins,
            num_annotated_proteins=num_annotated_proteins,
            num_hypothetical_proteins=num_hypothetical_proteins
        )

        return genome_stats
