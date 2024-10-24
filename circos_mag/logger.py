
"""
Helper function for setting up logging to stdout and file.
"""

import os
import sys
import logging
import ntpath
import argparse


def logger_setup(log_dir: str, log_file: str, program_name: str, version: str, silent: bool) -> None:
    """Setup loggers.

    Logging information is written to stdout and a log file
    if the log_dir is not None. The logger is named 'timestamp' 
    and provides a timestamp with each call. Once you have called
    this function you can perform logging with:

    my_logger = logging.getLogger('timestamp')
    my_logger.info('Hello, world!'

    Parameters
    ----------
    log_dir : str
        Output directory for log file.
    log_file : str
        Desired name of log file.
    program_name : str
        Name of program.
    version : str
        Program version number.
    silent : boolean
        Flag indicating if output to stdout should be suppressed.
    """

    if logging.getLogger('timestamp').hasHandlers():
        # create `timestamp` logger only if it hasn't already been created
        return

    # setup general properties of loggers
    logger = logging.getLogger('timestamp')
    logger.setLevel(logging.DEBUG)
    log_format = logging.Formatter(fmt="[%(asctime)s] %(levelname)s: %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S")

    # setup logging to console
    stream_logger = logging.StreamHandler(sys.stdout)
    stream_logger.setFormatter(log_format)
    logger.addHandler(stream_logger)

    logger.is_silent = False
    if silent:
        logger.is_silent = True
        stream_logger.setLevel(logging.ERROR)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        timestamp_file_logger = logging.FileHandler(
            os.path.join(log_dir, log_file), 'a')
        timestamp_file_logger.setFormatter(log_format)
        logger.addHandler(timestamp_file_logger)

    logger.info(f'{program_name} v{version}')
    logger.info(ntpath.basename(sys.argv[0]) + ' ' + ' '.join(sys.argv[1:]))


class ChangeTempAction(argparse.Action):
    """Action for changing the directory used for temporary files.

    Example usage:
        <parse>.add_argument('--tmp_dir', action=ChangeTempAction, default=tempfile.gettempdir(), help='set temporary directory')
    """

    def __call__(self, parser, namespace, values, option_str=None):
        if os.path.isdir(values):
            tempfile.tempdir = values
            setattr(namespace, self.dest, values)
        else:
            raise argparse.ArgumentTypeError(
                f'The value of {option_str} must be a valid directory.')


class CustomHelpFormatter(argparse.HelpFormatter):
    """Provide a customized format for CLI help output.

    http://stackoverflow.com/questions/9642692/argparse-help-without-duplicate-allcaps
    """

    def _get_help_string(self, action):
        """Place default value in help string."""
        h = action.help
        if '%(default)' not in action.help:
            if action.default != '' and action.default != [] and action.default is not None and not isinstance(action.default, bool):
                if action.default is not argparse.SUPPRESS:
                    defaulting_nargs = [
                        argparse.OPTIONAL, argparse.ZERO_OR_MORE]

                    if action.option_strings or action.nargs in defaulting_nargs:
                        if '\n' in h:
                            lines = h.splitlines()
                            lines[0] += ' (default: %(default)s)'
                            h = '\n'.join(lines)
                        else:
                            h += ' (default: %(default)s)'
            return h

    def _format_action_invocation(self, action):
        """Removes duplicate ALLCAPS with positional arguments."""
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)

                return '%s %s' % (', '.join(parts), args_string)

            return ', '.join(parts)

    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()

    def _get_default_metavar_for_positional(self, action):
        return action.dest
