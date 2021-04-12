#!/usr/bin/env python3
"""
Copyright 2021 Ryan Wick (rrwick@gmail.com)
https://github.com/rrwick/Poligner

This file is part of Poligner. Poligner is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. Poligner is distributed
in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with Poligner.
If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import random
import sys

from .alignment import align_reads, output_alignments_to_stdout
from .help_formatter import MyParser, MyHelpFormatter
from .insert_size import get_insert_size_distribution, select_alignments_using_insert_size, \
    final_alignment_selection, set_sam_flags
from .log import bold
from .mask_reads import mask_read_sequences
from .informative_positions import find_informative_positions, \
    select_alignments_using_informative_positions
from .misc import get_default_thread_count, check_python_version, get_ascii_art
from .version import __version__


def main():
    check_python_version()
    args = parse_args()
    random.seed(0)
    alignments, read_pair_names, read_count, header_lines = \
        align_reads(args.target, args.short1, args.short2, args.threads, args.max_errors)
    insert_size_distribution = get_insert_size_distribution(alignments)
    select_alignments_using_insert_size(alignments, insert_size_distribution,
                                        read_pair_names, read_count)
    mask_read_sequences(read_pair_names, alignments, args.target)
    informative_positions = find_informative_positions(read_pair_names, alignments, args.target)
    select_alignments_using_informative_positions(alignments, informative_positions,
                                                  read_pair_names, read_count)
    final_alignment_selection(alignments, insert_size_distribution, read_pair_names, read_count)
    set_sam_flags(alignments, read_pair_names, insert_size_distribution)
    output_alignments_to_stdout(alignments, read_pair_names, header_lines)


def parse_args():
    description = 'R|' + get_ascii_art() + '\n' + \
                  bold('Poligner: a tool for aligning short reads to a long-read assembly')
    parser = MyParser(description=description, formatter_class=MyHelpFormatter, add_help=False)

    required_args = parser.add_argument_group('Required arguments')
    required_args.add_argument('-x', '--target', type=str, required=True,
                               help='Alignment target (a long-read assembled genome in FASTA '
                                    'format)')
    required_args.add_argument('-1', '--short1', type=str, required=True,
                               help='Input short reads, first in pair (FASTQ format)')
    required_args.add_argument('-2', '--short2', type=str, required=True,
                               help='Input short reads, second in pair (FASTQ format)')

    setting_args = parser.add_argument_group('Settings')
    setting_args.add_argument('-m', '--max_errors', type=int, default=20,
                              help='Ignore alignments with more than this number of mismatches '
                                   'and indels')
    setting_args.add_argument('-t', '--threads', type=int, default=get_default_thread_count(),
                              help='Number of threads')

    help_args = parser.add_argument_group('Help')
    help_args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                           help='Show this help message and exit')
    help_args.add_argument('--version', action='version', version='Poligner v' + __version__,
                           help="Show program's version number and exit")

    # If no arguments were used, print the base-level help which lists possible commands.
    if len(sys.argv) == 1:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    return parser.parse_args()


if __name__ == '__main__':
    main()
