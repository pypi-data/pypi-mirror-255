import os,sys,re
import collections
import argparse
from pathlib import Path
from TPEA import parsers
def main():
    args = parsers.parse_args(sys.argv[1:])
    if args.command == "MAP16S":
        from TPEA.classify import SRRCLASS
        try:
            SRRCLASS(args.SRR,args.SILVA,args.CPU,args.TaxB,args.RefID)
        except:
            sys.exit(1)
if __name__=='__main__':
    main()