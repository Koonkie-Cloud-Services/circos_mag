"""
Generate Circos plot for MAG.
"""

import os
import shutil
import logging
import dataclasses

from circos_mag.karyotype import Karyotype
from circos_mag.gc import GC
from circos_mag.rrna import rRNA
from circos_mag.trna import tRNA
from circos_mag.coverage import Coverage
from circos_mag.execute import execute
from circos_mag.plot_style import PlotStyle
import circos_mag.seq_io as seq_io
import circos_mag.defaults as Defaults


class CircosPlot():
    """Generate Circos plot for MAG."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def customize_tick_conf(self, genome_file, output_dir):
        """Customize tick config file to exclude short contigs."""

        # get list of short contigs
        short_contigs = []
        for contig_id, contig in seq_io.read_seq(genome_file):
            if len(contig) < Defaults.MIN_CONTIG_LEN_FOR_TICKS:
                short_contigs.append(f'-{contig_id}')

        # read tick config file
        tick_config_file = os.path.join(output_dir, 'ticks.conf')
        tick_config = open(tick_config_file).readlines()

        # write out modified tick config file
        fout = open(tick_config_file, 'w')
        for line in tick_config:
            if line.startswith('</ticks>'):
                chrom_str = ';'.join(short_contigs)
                fout.write(f'chromosomes = {chrom_str}\n')

            fout.write(line)

        fout.close()

    def customize_circos_config(self, config_file: str, plot_style: PlotStyle, attribute_prefix: str) -> None:
        """Customize Circos config file with specified attributes."""

        # read config file
        config_data = open(config_file).readlines()

        # get fields in plot style
        plot_style_dict = dataclasses.asdict(plot_style)

        # write out customized config file
        fout = open(config_file, 'w')
        for line in config_data:
            if '=' in line:
                attr, value = [t.strip() for t in line.strip().split('=')]

                custom_attr = f'{attribute_prefix}_{attr}'
                if custom_attr in plot_style_dict:
                    value = plot_style_dict[custom_attr]

                line = f'{attr} = {value}\n'

            fout.write(line)

        fout.close()

    def plot(self,
             genome_file: str,
             gff_file: str,
             coverage_file: str,
             plot_style_file: str,
             completeness: float,
             min_contig_len: int,
             max_contigs: int,
             output_dir: str) -> None:
        """Generate Circos plot for MAG."""

        circos_out_dir = os.path.join(output_dir, 'circos')
        os.makedirs(circos_out_dir, exist_ok=True)

        # get plot style
        plot_style = PlotStyle()
        if plot_style_file is not None:
            plot_style.from_toml_file(plot_style_file)

        # create Karyotype file for MAG
        self.logger.info('Creating Karyotype file for MAG:')
        karyotype = Karyotype()
        genome_stats = karyotype.create(genome_file,
                                        gff_file,
                                        completeness,
                                        min_contig_len,
                                        max_contigs,
                                        plot_style,
                                        circos_out_dir)
        self.logger.info(f' - genome size = {genome_stats.genome_size}')
        self.logger.info(f' - contigs = {genome_stats.num_contigs}')
        self.logger.info(f' - N50 = {genome_stats.n50_contigs}')
        self.logger.info(f' - L50 = {genome_stats.l50_contigs}')
        self.logger.info(f' - annotated proteins = {genome_stats.num_annotated_proteins}')
        self.logger.info(f' - hypothetical proteins = {genome_stats.num_hypothetical_proteins}')
        if genome_stats.num_filtered_contigs > 0:
            self.logger.info(f' - number filtered contigs = {genome_stats.num_filtered_contigs}')

        # calculate GC-content over contigs in MAGs
        self.logger.info('Calculating GC content across contigs:')
        gc = GC()
        mean_gc = gc.create(genome_file, plot_style, circos_out_dir)
        self.logger.info(f' - mean GC = {mean_gc:.1f}%')

        # determine position of rRNA genes
        self.logger.info('Determining position of rRNA genes:')
        rrna = rRNA()
        rrna_counts = rrna.create(gff_file, plot_style, circos_out_dir)
        for rrna_type, count in rrna_counts.items():
            self.logger.info(f' - {rrna_type} = {count}')

        # determine position of tRNA genes
        self.logger.info('Determining position of tRNA genes:')
        trna = tRNA()
        trna_counts = trna.create(gff_file, plot_style, circos_out_dir)

        total_trnas = 0
        unique_trans = set()
        for trna_type, count in trna_counts.items():
            self.logger.info(f' - {trna_type} = {count}')
            total_trnas += count

            # assuming tRNA annotations have the format: tRNA-Lys(ttt)
            unique_trans.add(trna_type.split('(')[0])

        self.logger.info(f' - identified {total_trnas:,} tRNAs for {len(unique_trans):,} amino acids')

        # calculate coverage across contigs
        if coverage_file is not None:
            self.logger.info('Calculating coverage across contigs:')
            coverage = Coverage()
            mean_coverage, _contig_coverage = coverage.create(genome_file,
                                                              coverage_file,
                                                              plot_style,
                                                              circos_out_dir)
            self.logger.info(f' - mean coverage = {mean_coverage:.1f}')
        else:
            # need to create empty coverage file for Circos to execute
            cov_file = os.path.join(circos_out_dir, 'coverage.tsv')
            open(cov_file, 'a').close()
            mean_coverage = None

        # copy default config files
        self.logger.info('Copying Circos configuration files.')
        for f in os.listdir(Defaults.CIRCOS_CONFIG_FILE_DIR):
            shutil.copyfile(os.path.join(Defaults.CIRCOS_CONFIG_FILE_DIR, f),
                            os.path.join(circos_out_dir, f))

        # customize the ticks.conf file to exclude drawing
        # ticks on short contigs
        self.customize_tick_conf(genome_file, circos_out_dir)
        self.customize_circos_config(os.path.join(circos_out_dir, 'gc.conf'), plot_style, 'gc')
        self.customize_circos_config(os.path.join(circos_out_dir, 'coverage.conf'), plot_style, 'cov')
        self.customize_circos_config(os.path.join(circos_out_dir, 'rrna.conf'), plot_style, 'rrna')
        self.customize_circos_config(os.path.join(circos_out_dir, 'trna.conf'), plot_style, 'trna')

        # create Circos plot
        self.logger.info('Creating Circos plot.')
        cmd = ['circos']
        cmd += ['--config', os.path.join(circos_out_dir, 'circos.conf')]
        execute(cmd, program='Circos')

        # move plot to output directory since Circos will create
        # these in the current working directory
        shutil.move('circos.png', os.path.join(output_dir, 'circos.png'))
        shutil.move('circos.svg', os.path.join(output_dir, 'circos.svg'))

        # create file with genome statistics
        fout = open(os.path.join(output_dir, 'genome_stats.tsv'), 'w')
        fout.write('[Assembly Statistics]\n')
        fout.write(f'Genome size = {genome_stats.genome_size}\n')
        fout.write(f'No. contigs = {genome_stats.num_contigs}\n')
        fout.write(f'N50 (contigs) = {genome_stats.n50_contigs}\n')
        fout.write(f'L50 (contigs) = {genome_stats.l50_contigs}\n')
        fout.write(f'GC = {mean_gc:.3f}\n')
        if mean_coverage:
            fout.write(f'Coverage = {mean_coverage:.3f}\n')
        fout.write(f'No. CDS = {genome_stats.num_cds}\n')
        fout.write(f'No. annotated proteins = {genome_stats.num_annotated_proteins}\n')
        fout.write(f'No. hypothetical proteins = {genome_stats.num_hypothetical_proteins}\n')
        if genome_stats.num_filtered_contigs > 0:
            fout.write(f'No. filtered contigs = {genome_stats.num_filtered_contigs}\n')

        fout.write('\n[rRNA Statistics]\n')
        for rrna_type, count in rrna_counts.items():
            fout.write(f'{rrna_type} = {count}\n')

        fout.write('\n[tRNA Statistics]\n')
        fout.write(f'No. tRNAs = {total_trnas}\n')
        fout.write(f'No. unique tRNAs = {len(unique_trans)}\n')
        for trna_type, count in trna_counts.items():
            fout.write(f'{trna_type} = {count}\n')

        fout.close()
