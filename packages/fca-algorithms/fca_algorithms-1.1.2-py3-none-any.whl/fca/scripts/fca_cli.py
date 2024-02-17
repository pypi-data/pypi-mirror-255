#!/usr/bin/env python

import os
import argparse

from ..__version__ import __version__
from ..plot.plot import plot_lattices
from ..rca.rca import rca_get_relations
from ..rca.p18n import Operators
from .import_utils import *
from .export_utils import *


INVALID_FILETYPE_MSG = "Error: Invalid file format. {} must be a .txt file."
INVALID_PATH_MSG = "Error: Invalid file path/name. Path {} does not exist."
MANDATORY_ARGUMENTS_MSG = "Either -c or -k params should be specified"


def validate_file(file_name):
    """
    validate file name and path.
    """
    if not valid_path(file_name):
        SystemExit(INVALID_PATH_MSG.format(file_name))
    elif not valid_filetype(file_name):
        SystemExit(INVALID_FILETYPE_MSG.format(file_name))
    return


def valid_filetype(file_name):
    # validate file type
    return file_name.endswith(".csv")


def valid_path(path):
    # validate file path
    return os.path.exists(path)


def main():
    # create a parser object
    parser = argparse.ArgumentParser(description="FCA cli")

    # add argument
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    parser.add_argument(
        "-c",
        "--context",
        type=str,
        nargs="?",
        metavar="context_name",
        help="Formal context csv file.",
    )

    parser.add_argument(
        "-fc",
        "--context-format",
        type=str,
        metavar="context_format",
        choices=(
            "one_line_per_attribute",
            "table",
        ),
        default="one_line_per_attribute",
        help="Formal context csv file format.",
    )

    parser.add_argument(
        "-k",
        "--contexts",
        type=str,
        nargs="*",
        metavar="context_names",
        help="Formal contexts csv files from the relational context family.",
    )

    parser.add_argument(
        "-r",
        "--relations",
        type=str,
        nargs="*",
        metavar="relation_file_names",
        help="Relation csv filename in case of RCA. Name is expected to be r_1_3.csv for example if its a "
        "relation between objects of the contexts 1 and 3 respectively"
        "  On the other hand, in each row we expect to have the tuple separated by comma e.g., 1,2,3 "
        "  for a relation between the first, second and third object",
    )

    parser.add_argument(
        "--show_hasse",
        action="store_true",
        help="If present, the tool will show the hasse diagram",
    )

    parser.add_argument(
        "--show_objects",
        action="store_true",
        help="If present, the hasse will show also the objects",
    )

    parser.add_argument(
        "--hasse_file_name",
        type=str,
        nargs="?",
        metavar="hasse_file_name",
        help="Specifies the name the hasse file will have \n"
        "Supported formats: .dot, and .gexf",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default=".",
        help="Output folder in which the csvs should be written.",
    )

    parser.add_argument(
        "-o",
        "--operator",
        type=str,
        choices=(
            "exists",
            "forall",
        ),
        default="exists",
        help="P18n operator to use in the graduation process",
    )

    parser.add_argument(
        "--edge_colours",
        type=str,
        nargs="*",
        metavar="edge_colours",
        help="Colours for the relational edges. If the maximum arity is k, we expect k or less colours."
        " The rest are going to be chosen randomly",
    )

    # parse the arguments from standard input
    args = parser.parse_args()

    if args.contexts:
        K, R, edge_colours = parse_rca(args)
        rho = Operators[args.operator]
        lattices = rca_get_relations(K, R, rho)
        for i, lattice in enumerate(lattices):
            export_to_file(i, lattice, args.output_dir)
        if args.show_hasse:
            plot_lattices(lattices, edge_colours=edge_colours)
    elif args.context:
        K = parse_fca(args)
        lattice = K.get_lattice()
        if args.show_hasse:
            lattice.plot(
                only_attributes=not args.show_objects, save_plot=args.hasse_file_name
            )
        export_to_file(0, lattice, args.output_dir)
    elif args.version:
        args.run(args)
    else:
        raise SystemExit(MANDATORY_ARGUMENTS_MSG)


if __name__ == "__main__":
    main()
