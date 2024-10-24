"""
Methods for reading and writing FASTA/Q files.

All functions support reading and writing of Gzip compressed files as determined by
files ending in `.gz`. 
"""

import os
import sys
import gzip
import random
import traceback
from typing import Tuple, Dict


def read(seq_file: str) -> Dict[str, str]:
    """Read sequences from fasta/q file.

    Parameters
    ----------
    seq_file : str
        Name of fasta/q file to read.

    Returns
    -------
    dict : dict[seq_id] -> seq
        Sequences indexed by sequence id.
    """
    _prefix, ext = os.path.splitext(seq_file)
    if ext == ".gz":
        _prefix, ext = os.path.splitext(_prefix)
    
    if ext in ('.fq', '.fastq'):
        return read_fastq(seq_file)
    
    if ext in ('.fa', '.fasta', '.faa', '.fna'):
        return read_fasta(seq_file)
    
    print(traceback.format_exc())
    print(
        f"\n[Error] Unrecognized extension for sequence file: {seq_file}")
    sys.exit(1)


def read_fasta(fasta_file: str, keep_annotation: bool = False) -> Dict[str, str]:
    """Read sequences from fasta file.

    Parameters
    ----------
    fasta_file : str
        Name of fasta file to read.
    keep_annotation : boolean
        Determine is sequence id should contain annotation.

    Returns
    -------
    dict : dict[seq_id] -> seq
        Sequences indexed by sequence id.
    """

    if not os.path.exists(fasta_file):
        raise FileNotFoundError(f'Input file {fasta_file} does not exist.')

    if os.stat(fasta_file).st_size == 0:
        return {}

    try:
        open_file = open
        if fasta_file.endswith('.gz'):
            open_file = gzip.open

        seqs = {}
        for line in open_file(fasta_file, 'rt'):
            # skip blank lines
            if not line.strip():
                continue

            if line[0] == '>':
                if keep_annotation:
                    seq_id = line[1:-1]
                else:
                    seq_id = line[1:].split(None, 1)[0]

                seqs[seq_id] = []
            else:
                seqs[seq_id].append(line.strip())

        for seq_id, seq in seqs.items():
            seqs[seq_id] = ''.join(seq).replace(' ', '')
    except Exception as _e:
        print(traceback.format_exc())
        print(f"\n[Error] Failed to process sequence file: {fasta_file}")
        sys.exit(1)

    return seqs


def read_fastq(fastq_file: str) -> Dict[str, str]:
    """Read sequences from fastq file.

    Parameters
    ----------
    fastq_file : str
        Name of fastq file to read.

    Returns
    -------
    dict : dict[seq_id] -> seq
        Sequences indexed by sequence id.
    """

    if not os.path.exists(fastq_file):
        raise FileNotFoundError(f'Input file {fastq_file} does not exist.')

    if os.stat(fastq_file).st_size == 0:
        return {}

    try:
        open_file = open
        if fastq_file.endswith('.gz'):
            open_file = gzip.open

        seqs = {}
        line_num = 0
        for line in open_file(fastq_file, 'rt'):
            line_num += 1

            if line_num == 1:
                seq_id = line[1:].split(None, 1)[0]
            elif line_num == 2:
                seqs[seq_id].seq = line.strip()
            elif line_num == 4:
                line_num = 0
    except Exception as _e:
        print(traceback.format_exc())
        print(f"\n[Error] Failed to process sequence file: {fastq_file}")
        sys.exit(1)

    return seqs


def read_seq(seq_file: str, keep_annotation: bool = False) -> Dict[str, str]:
    """Generator function to read sequences from fasta/q file.

    This function is intended to be used as a generator
    in order to avoid having to have large sequence files
    in memory. Input file may be gzipped and in either
    fasta or fastq format. It is slightly more efficient
    to directly call read_fasta_seq() or read_fastq_seq()
    if the type of input file in known.

    Example:
    seq_io = SeqIO()
    for seq_id, seq in seq_io.read_seq(fasta_file):
        print seq_id
        print seq

    Parameters
    ----------
    seq_file : str
        Name of fasta/q file to read.
    keep_annotation : boolean
        Determine if annotation string should be returned.

    Yields
    ------
    list : [seq_id, seq, [annotation]]
        Unique id of the sequence followed by the sequence itself,
        and the annotation if keep_annotation is True.
    """
    _prefix, ext = os.path.splitext(seq_file)
    if ext == ".gz":
        _prefix, ext = os.path.splitext(_prefix)
    if ext in ('.fq', '.fastq'):
        for rtn in read_fastq_seq(seq_file):
            yield rtn
    elif ext in ('.fa', '.fasta', '.faa', '.fna'):
        for rtn in read_fasta_seq(seq_file, keep_annotation):
            yield rtn
    else:
        print(traceback.format_exc())
        print(
            f"\n[Error] Unrecognized extension for sequence file: {seq_file}")
        sys.exit(1)


def read_fasta_seq(fasta_file: str, keep_annotation: bool = False) -> Dict[str, str]:
    """Generator function to read sequences from fasta file.

    This function is intended to be used as a generator
    in order to avoid having to have large sequence files
    in memory. Input file may be gzipped.

    Example:
    seq_io = SeqIO()
    for seq_id, seq in seq_io.read_fasta_seq(fasta_file):
        print seq_id
        print seq

    Parameters
    ----------
    fasta_file : str
        Name of fasta file to read.
    keep_annotation : boolean
        Determine if annotation string should be returned.

    Yields
    ------
    list : [seq_id, seq, [annotation]]
        Unique id of the sequence followed by the sequence itself,
        and the annotation if keep_annotation is True.
    """

    if not os.path.exists(fasta_file):
        raise FileNotFoundError(f'Input file {fasta_file} does not exist.')

    if os.stat(fasta_file).st_size == 0:
        pass

    try:
        open_file = open
        if fasta_file.endswith('.gz'):
            open_file = gzip.open

        seq_id = None
        annotation = None
        seq = None
        for line in open_file(fasta_file, 'rt'):
            # skip blank lines
            if not line.strip():
                continue

            if line[0] == '>':
                if seq_id is not None:
                    if keep_annotation:
                        yield seq_id, ''.join(seq).replace(' ', ''), annotation
                    else:
                        yield seq_id, ''.join(seq).replace(' ', '')

                line_split = line[1:-1].split(None, 1)
                if len(line_split) == 2:
                    seq_id, annotation = line_split
                else:
                    seq_id = line_split[0]
                    annotation = ''
                seq = []
            else:
                seq.append(line.strip())

        if seq is None:
            raise TypeError(
                f"\n[Error] Input FASTA file is empty: {fasta_file}")

        # report last sequence
        if keep_annotation:
            yield seq_id, ''.join(seq).replace(' ', ''), annotation
        else:
            yield seq_id, ''.join(seq).replace(' ', '')
    except GeneratorExit:
        pass
    except Exception as _e:
        print(traceback.format_exc())
        print(f"\n[Error] Failed to process sequence file: {fasta_file}")
        sys.exit(1)


def read_fastq_seq(fastq_file: str) -> Dict[str, str]:
    """Generator function to read sequences from fastq file.

    This function is intended to be used as a generator
    in order to avoid having to have large sequence files
    in memory. Input file may be gzipped.

    Example:
    seq_io = SeqIO()
    for seq_id, seq in seq_io.read_fastq_seq(fastq_file):
        print seq_id
        print seq

    Parameters
    ----------
    fastq_file : str
        Name of fastq file to read.

    Yields
    ------
    list : [seq_id, seq]
        Unique id of the sequence followed by the sequence itself.
    """

    if not os.path.exists(fastq_file):
        raise FileNotFoundError(f'Input file {fastq_file} does not exist.')

    if os.stat(fastq_file).st_size == 0:
        pass

    try:
        open_file = open
        if fastq_file.endswith('.gz'):
            open_file = gzip.open

        line_num = 0
        for line in open_file(fastq_file, 'rt'):
            line_num += 1

            if line_num == 1:
                seq_id = line[1:].split(None, 1)[0]
            elif line_num == 2:
                yield seq_id, line.strip()
            elif line_num == 4:
                line_num = 0
    except GeneratorExit:
        pass
    except  Exception as _e:
        print(traceback.format_exc())
        print(f"\n[Error] Failed to process sequence file: {fastq_file}")
        sys.exit(1)


def write_fasta(seqs: Dict[str, str], output_file: str) -> None:
    """Write sequences to fasta file.

    If the output file has the extension 'gz',
    it will be compressed using gzip.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence id.
    output_file : str
        Name of fasta file to produce.
    """

    if output_file.endswith('.gz'):
        fout = gzip.open(output_file, 'wt')
    else:
        fout = open(output_file, 'w')

    for seq_id, seq in seqs.items():
        fout.write('>{}\n{}\n'.format(seq_id, seq))

    fout.close()


def write_fastq(seqs: Dict[str, Tuple[str, str]], output_file: str) -> None:
    """Write sequences to fasta file.

    If the output file has the extension 'gz',
    it will be compressed using gzip.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence id.
    output_file : str
        Name of fasta file to produce.
    """

    if output_file.endswith('.gz'):
        fout = gzip.open(output_file, 'wt')
    else:
        fout = open(output_file, 'w')

    for seq_id, seq_record in seqs.items():
        fout.write("@{}\n{}\n+\n{}\n".format(seq_id,
                   seq_record[0], seq_record[1]))

    fout.close()


def simulate_nuc_sequences(n_seqs: int, file_format="fasta", seq_len=80, record_prefix="Sequence_") -> dict:
    """Simulate nucleotide sequences and quality scores for fasta or fastq sequence records."""
    seq_records = {}
    nuc_alpha = "ACGT"
    qual_chars = ''.join(chr(i) for i in range(128))[33:-1]
    if file_format == "fasta":
        for i in range(0, n_seqs):
            seq_records[record_prefix + str(i)] = ''.join(
                random.choice(nuc_alpha) for _ in range(seq_len))
    else:
        for i in range(0, n_seqs):
            seq_records[record_prefix + str(i)] = (''.join(random.choice(nuc_alpha) for _ in range(seq_len)),
                                                   ''.join(random.choice(qual_chars) for _ in range(seq_len)))

    return seq_records