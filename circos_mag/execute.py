"""
Functions for executing or checking for external programs.
"""

import os
import sys
import shutil
import logging
import subprocess
from typing import Optional, List


def run_bash(command: str):
    """Execute command via bash."""

    process = subprocess.run(["bash", "-c", command],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=None,
                             check=True,
                             encoding='utf-8')

    return process.stdout


def execute(cmd: List[str], program: str = None, capture: bool = False, silent: bool = False) -> str:
    """Execute external program.

    Parameters
    ----------
    cmd : list[str]
        Command to execute.
    program : str
        Add program name to output produced by external program.
    capture : bool
        Flag indicating whether the stdout and stderr of a program
        should be captured in a string and returned.
    silent : bool
        Suppress printing output from external program to console

    Returns
    -------
    str
        String with output of stdout and stderr if capture was set to True.
    """

    logger = logging.getLogger('timestamp')

    if not silent:
        logger.info(f"Executing: {' '.join(cmd)}")

    record = ""

    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='utf-8')

        while True:
            out = proc.stdout.readline()
            if not out and proc.poll() is not None:
                break

            if out.rstrip():
                if not silent:
                    if program:
                        logger.info(f'[{program}] {out.rstrip()}')
                    else:
                        logger.info(out.rstrip())

                if capture:
                    record += out

        if proc.returncode != 0:
            logger.error(f'Return code: {proc.returncode}')
            sys.exit(1)
    except OSError as e:
        print(e)
        logger.error('Failed to execute command.')
        sys.exit(1)

    return record


def decompress(input_file: str, output_file: str) -> None:
    """Decompress Gzip file.

    Parameters
    ----------
    input_file : str
        File to decompress.

    output_file : str
        Decompressed output file.    
    """

    check_on_path('pigz')

    logger = logging.getLogger('timestamp')

    cmd = ['pigz', '-cdk', input_file]

    logger.info(f"Executing: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                encoding='utf-8')

        fout = open(output_file, 'w')

        while True:
            out = proc.stdout.readline()
            if not out and proc.poll() is not None:
                break

            if out:
                fout.write(out)

        fout.close()

        if proc.returncode != 0:
            logger.error(f'Return code: {proc.returncode}')
            sys.exit(1)
    except OSError as e:
        print(e)
        logger.error('Failed to decompress file.')
        sys.exit(1)


def compress(input_file: str) -> str:
    """Gzip compress file.

    Parameters
    ----------
    input_file : str
        File to compress.

    Returns
    -------
    str
        Path of compressed file.
    """

    check_on_path('pigz')

    logger = logging.getLogger('timestamp')

    cmd = ['pigz', '-f', input_file]

    logger.info(f"Executing: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='utf-8')

        while True:
            out = proc.stdout.readline()
            if not out and proc.poll() is not None:
                break

        if proc.returncode != 0:
            logger.error(f'Return code: {proc.returncode}')
            sys.exit(1)
    except OSError as e:
        print(e)
        logger.error('Failed to compress file.')
        sys.exit(1)

    return input_file + '.gz'


def compress_dir(input_dir: str, remove_dir: bool = False) -> str:
    """Gzip compress directory.

    Parameters
    ----------
    input_dir : str
        Directory to compress.
    remove_dir : bool
        Flag indicating if directory should be deleted.

    Returns
    -------
    str
        Path of compressed directory file.
    """

    check_on_path('pigz')

    logger = logging.getLogger('timestamp')

    compressed_dir_file = f'{input_dir}.tar.gz'
    cmd = ['tar', '--use-compress-program=pigz',
           '-cf', compressed_dir_file, input_dir]

    logger.info(f"Executing: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='utf-8')

        while True:
            out = proc.stdout.readline()
            if not out and proc.poll() is not None:
                break

        if proc.returncode != 0:
            logger.error(f'Return code: {proc.returncode}')
            sys.exit(1)
    except OSError as e:
        print(e)
        logger.error('Failed to compress directory.')
        sys.exit(1)

    if remove_dir:
        shutil.rmtree(input_dir)

    return compressed_dir_file


def is_executable(file_path: str) -> bool:
    """Check if file is executable.

    Parameters
    ----------
    file_path : str
        Path to file.

    Returns
    -------
    boolean
        True if executable, else False.
    """

    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def which(program: str) -> Optional[str]:
    """Return path to program.

    This is a Python implementation of the linux
    command 'which'.

    http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python

    Parameters
    ----------
    program : str
        Name of executable for program.

    Returns
    -------
    str
        Path to executable, or None if it isn't on the path.
    """

    fpath, _fname = os.path.split(program)
    if fpath:
        if is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_executable(exe_file):
                return exe_file

    return None


def check_on_path(program: str, exit_on_fail: bool = True) -> bool:
    """Check if program is on the system path.

    Parameters
    ----------
    program : str
        Name of executable for program.
    exit_on_fail : boolean
        Exit program with error code 1 if program in not on path.

    Returns
    -------
    boolean
        True if program is on path, else False.
    """

    if which(program):
        return True

    if exit_on_fail:
        logger = logging.getLogger('timestamp')
        logger.error(f'{program} is not on the system path.')
        sys.exit(1)

    return False


def check_dependencies(programs: List[str], exit_on_fail: bool = True) -> bool:
    """Check if all required programs are on the system path.

    Parameters
    ----------
    programs : iterable
        Names of executable programs.
    exit_on_fail : boolean
        Exit program with error code -1 if any program in not on path.

    Returns
    -------
    boolean
        True if all programs are on path, else False.
    """

    for program in programs:
        if not check_on_path(program, exit_on_fail):
            return False

    return True