import os,sys,re
import collections
import argparse
from pathlib import Path
from TPEA import parsers
def main():
    args = parsers.parse_args(sys.argv[1:])
    if args.command == "SRRHISAT":
        from TPEA.classify import SRRHISAT
        try:
            SRRHISAT(args.SRR,args.SILVA,args.CPU)
        except:
            sys.exit(1)
    
    elif args.command == "MAP16S":
        from TPEA.classify import SRRCLASS
        try:
            SRRCLASS(args.SRR,args.TaxB,args.RefID)
        except:
            sys.exit(1)
if __name__=='__main__':
    main()