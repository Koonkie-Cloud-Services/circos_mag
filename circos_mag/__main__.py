
#!/usr/bin/env python3

"""
Generate Circos plot for a MAG.
"""

import sys
import argparse
import logging
import traceback

from circos_mag import __version__, __prog_name__, __description__
from circos_mag.logger import logger_setup, CustomHelpFormatter
from circos_mag.main import ProgramRunner
import circos_mag.defaults as Defaults


def print_help():
    print(f'''

              ...::: Circos MAG v{__version__} :::...

    plot -> Create Circos plot for MAG.

  Use: circos_mag <command> -h for command specific help
    ''')


def add_standard_opt(parser):
    """Add in standard set of additional arguments."""

    parser.add_argument('-h', '--help', action='help',
                        help='show this help message and exit')


def add_plot_subcommand(subparsers):
    """Add plot subcommand CLI."""

    parser = subparsers.add_parser('plot',
                                   formatter_class=CustomHelpFormatter,
                                   description='Create Circos plot for MAG..',
                                   add_help=False)

    req = parser.add_argument_group("required arguments")
    req.add_argument('--genome_file',
                     required=True,
                     help="genomic FASTA file for MAG")
    req.add_argument('--gff_file',
                     required=True,
                     help="gene feature file (GFF) indicating gene annotations, tRNAs, and rRNAs")
    req.add_argument('-o', '--output_dir',
                     required=True,
                     help="output directory")

    opt = parser.add_argument_group("optional arguments")
    opt.add_argument('--coverage_file',
                     help="file indicating coverage of each base of contigs in genome (must include zeros!)")
    opt.add_argument('--completeness',
                     help="completeness estimate of genome [0, 100]; used to draw visual indication of `missing` DNA",
                     type=float,
                     default=100.0)
    opt.add_argument('--min_contig_len',
                     help="minimum length of contig to include in Circos plot",
                     type=int,
                     default=Defaults.MIN_CONTIG_LEN)
    opt.add_argument('--max_contigs',
                     help="maximum number of contigs to include in Circos plot (from longest to shortest)",
                     type=int,
                     default=Defaults.MAX_CONTIGS)
    opt.add_argument('--gc_window_size',
                     help="size in base pairs of the window used to calculate GC content across a contig",
                     type=int,
                     default=Defaults.GC_WINDOW_SIZE)
    opt.add_argument('--cov_window_size',
                     help="size in base pairs of the window used to calculate coverage across a contig",
                     type=int,
                     default=Defaults.COV_WINDOW_SIZE)
    add_standard_opt(opt)


def get_cli_parser():
    """Setup and return CLI."""

    parser = argparse.ArgumentParser('circos_mag', add_help=False)
    subparsers = parser.add_subparsers(help="--", dest='subparser_name')

    add_plot_subcommand(subparsers)

    return parser


def main():
    """Generate Circos plot for a MAG."""

    # check if user is requesting help or version information
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--h', '-help', '--help'}:
        print_help()
        sys.exit(0)
    elif sys.argv[1] in {'-v', '--v', '-version', '--version'}:
        print(f"{__prog_name__}: version {__version__}")
        sys.exit(0)
    else:
        args = get_cli_parser().parse_args()

    # setup logger
    logger_setup(None,
                 __prog_name__ + '.log',
                 __prog_name__,
                 __version__,
                 args.silent if hasattr(args, 'silent') else False)

    logger = logging.getLogger('timestamp')
    logger.info(__prog_name__ + ' v' + __version__ + ': ' + __description__)

    # perform action specified via CLI
    try:
        p = ProgramRunner()
        p.run(args)
    except SystemExit:
        logger.error(
            'Controlled exit resulting from early termination.')
        sys.exit(1)
    except KeyboardInterrupt:
        logger.error(
            'Controlled exit resulting from interrupt signal.')
        sys.exit(1)
    except Exception as e:
        msg = 'Uncontrolled exit resulting from an unexpected error.\n\n'
        msg += '=' * 80 + '\n'
        msg += '  MESSAGE: {}\n'.format(e)
        msg += '_' * 80 + '\n\n'
        msg += traceback.format_exc()
        msg += '=' * 80
        logger.error(msg)
        sys.exit(1)

    logger.info('Done.')


if __name__ == '__main__':
    main()
