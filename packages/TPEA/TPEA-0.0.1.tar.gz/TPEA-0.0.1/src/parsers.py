"""Argument parsers."""

import argparse
import sys

from TPEA import __version__

def add_MAP16S_subparser(subparsers):
    parser = subparsers.add_parser(
        "MAP16S",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $ PEA MAP16S --SRR SRR16092814 --SILVA SILVA_Bacteria --CPU 10 --TaxB tax_slv_ssu_138.bacteria.txt --RefID SILVA_138.1_used_tax_silva.ID_List\n"
        "  Output: SRR16092814.class1 and SRR16092814.class2\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--SILVA",
        help="INDEX of 16S genes, e.g., SILVA_Bacteria",
        type=str,
    )
    
    parser.add_argument(
        "--CPU",
        default="10",
        help="Number of CPU",
        type=int,
    )
    
    parser.add_argument(
        "--TaxB",
        default="tax_slv_ssu_138.bacteria.txt",
        help="tax",
        type=str,
    )
    
    parser.add_argument(
        "--RefID",
        default="SILVA_138.1_used_tax_silva.ID_List",
        help="tax",
        type=str,
    )

def get_parser():
    parser = argparse.ArgumentParser(
        "TPEA",
        description="TPEA: Toolkits for Plant Endophyte Analyses",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    subparsers = parser.add_subparsers(dest="command")
    add_MAP16S_subparser(subparsers)
    return parser

def parse_args(args):
    parser = get_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        parser.exit(1)

    return args