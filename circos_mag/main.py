"""
Handle execution of Circos MAG subcommands.
"""

import os
import sys
import logging

from circos_mag.circos_plot import CircosPlot


class ProgramRunner():
    """Handle execution of Circos MAG subcommands.."""

    def __init__(self):
        """Initialization."""

        self.logger = logging.getLogger('timestamp')

    def plot(self, args) -> None:
        """Create Circos plot for MAG."""

        self.logger.info('Creating Circos plot.')

        os.makedirs(args.output_dir, exist_ok=True)

        p = CircosPlot()
        p.plot(args.genome_file,
               args.gff_file,
               args.coverage_file,
               args.completeness,
               args.min_contig_len,
               args.max_contigs,
               args.gc_window_size,
               args.cov_window_size,
               args.output_dir)

    def run(self, args) -> None:
        """Parse CLI args and run specified subcommand."""

        if args.subparser_name == 'plot':
            self.plot(args)
        else:
            self.logger.error(
                f'Unknown command: {args.subparser_name}\n')
            sys.exit(1)
