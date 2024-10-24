"""
Functions for calculating common statistics or transformations of DNA sequence strings.
"""

from typing import Tuple, Dict

from circos_mag.seq_io import read_seq


def contig_lengths(seqs: Dict[str, str]) -> Dict[str, int]:
    """Read contig length from genomic FASTA file and return in descending order."""

    contigs = {}
    for contig_id, contig in seqs.items():
        contigs[contig_id] = len(contig)

    return contigs


def seq_stats(seq_file: str) -> Tuple[int, int]:
    """Count number of sequences and bases in a FASTA/Q file."""

    num_seqs = 0
    num_bases = 0
    for _, seq in read_seq(seq_file):
        num_seqs += 1
        num_bases += len(seq)

    return num_seqs, num_bases


def count_seqs(seq_file: str) -> int:
    """Count the number of sequences in a FASTA/Q file."""

    return sum(1 for _, _ in read_seq(seq_file))


def count_nt(seq: str) -> Tuple[int, int, int, int]:
    """Count occurrences of each nucleotide in a sequence.

    Only the bases A, C, G, and T(U) are counted. Ambiguous
    bases are ignored.
    """

    s = seq.upper()
    a = s.count('A')
    c = s.count('C')
    g = s.count('G')
    t = s.count('T') + s.count('U')

    return a, c, g, t


def gc(seq: str) -> float:
    """Calculate GC content of a sequence.

    GC is calculated as (G+C)/(A+C+G+T), where
    each of these terms represents the number
    of nucleotides within the sequence. Ambiguous
    and degenerate bases are ignored. Uracil (U)
    is treated as a thymine (T).
    """

    a, c, g, t = count_nt(seq)
    total_bases = (a + c + g + t)

    if total_bases == 0:
        return 0

    return float(g + c) / total_bases


def gc_of_seqs(seqs: Dict[str, str]) -> float:
    """Calculate GC content of a set of sequence."""

    total_a = 0
    total_c = 0
    total_g = 0
    total_t = 0

    for seq in seqs.values():
        a, c, g, t = count_nt(seq)
        total_a += a
        total_c += c
        total_g += g
        total_t += t

    return float(total_g + total_c) / (total_a + total_c + total_g + total_t)


def ambiguous_nucleotides(seq: str) -> int:
    """Count ambiguous or degenerate nucleotides in a sequence.

    Any base that is not a A, C, G, or T/U is considered
    to be ambiguous or degenerate.
    """

    a, c, g, t = count_nt(seq)

    return len(seq) - (a + c + g + t)


def N50_L50(seqs: Dict[str, str]) -> Tuple[int, int]:
    """Calculate N50 and L50 for a set of sequences.

     N50 is defined as the length of the longest
     sequence, L, for which 50% of the total bases
     are present in sequences of length >= L.

     L50 is the smallest number of sequences required 
     to achieve N50.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence ids.

    Returns
    -------
    int
        N50 for the set of sequences.
    int
        L50 for the set of sequences.
    """

    if not seqs:
        raise ValueError('No sequences provided.')

    seq_lens = [len(x) for x in seqs.values()]
    threshold = sum(seq_lens) / 2.0

    seq_lens.sort(reverse=True)

    cur_sum = 0
    L50 = 0
    for seq_len in seq_lens:
        cur_sum += seq_len
        L50 += 1
        if cur_sum >= threshold:
            N50 = seq_len
            break

    return N50, L50


def mean_length(seqs: Dict[str, str]) -> float:
    """Calculate mean length of sequences.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence ids.

    Returns
    -------
    float
        Mean length of sequences.
    """

    total_len = sum([len(x) for x in seqs.values()])

    return float(total_len) / len(seqs)


def max_length(seqs: Dict[str, str]) -> int:
    """Identify longest sequence.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence ids.

    Returns
    -------
    int
        Length of longest sequence.
    """

    return max([len(x) for x in seqs.values()])


def identify_contigs(seqs: Dict[str, str], contig_break: str = 'NNNNNNNNNN') -> Dict[str, str]:
    """Break scaffolds into contigs.

    Parameters
    ----------
    seqs : dict[seq_id] -> seq
        Sequences indexed by sequence ids.

    contig_break : str
        Motif used to split scaffolds into contigs.

    Returns
    -------
    dict : dict[seq_id] -> seq
        Contigs indexed by sequence ids.
    """

    contigs = {}
    for seq_id, seq in seqs.items():
        seq = seq.upper()
        contig_count = 0
        for contig in seq.split(contig_break):
            contig = contig.strip('N')
            if contig:
                contigs[seq_id + '_c' + str(contig_count)] = contig
                contig_count += 1

    return contigs


def complement_nucs(nuc_str: str, ambiguity=False):
    comp_str = ""
    trans_map = {"A": "T", "T": "A", "C": "G", "G": "C", "U": "A", 'N': 'N',
                 "M": "K", "K": "M", "R": "Y", "Y": "R", "W": "W", "S": "S", "V": "B", "B": "V", "H": "D", "D": "H"}
    for c in nuc_str.upper():
        try:
            comp_str += trans_map[c]
        except KeyError as e:
            if c == '.' or c == '-':
                comp_str += c
            elif ambiguity:
                comp_str += 'N'
            else:
                raise KeyError(e)

    return comp_str


def reverse_complement(nuc_sequence: str):
    return complement_nucs(nuc_sequence[::-1])
