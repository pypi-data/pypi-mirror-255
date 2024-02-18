#!/usr/bin/env python3
import os,sys,re
import collections
import argparse
import numpy as np
from Bio import SeqIO
from itertools import islice
import logging

def handle():
    return None

def deleteDuplicatedElement(listA):
    return sorted(set(listA), key = listA.index)

def progress_bar(finished_number,tasks_numbers):
    percentage=round(int(finished_number)/int(tasks_numbers)*100)
    print("\rDone "+format('['+str(finished_number)+'/'+str(tasks_numbers)+']')+" {}%: ".format(percentage),"▋" * (percentage // 2), end="")
    sys.stdout.flush()
    if int(finished_number)==int(tasks_numbers):
        print("\n")

def SRRCLASS(SRR,SILVA,CPU,TaxB,RefID):
    ###Step1
    cmd='fastq-dump --gzip --skip-technical --readids --read-filter pass --dumpbase --split-3 -M 150 --clip '+str(SRR)
    logging.info('Downloading reads for '+str(SRR)+" by fastq-dump\n")
    os.system(cmd)
    read1=str(SRR)+'_pass_1.fastq.gz'
    read2=str(SRR)+'_pass_2.fastq.gz'
    ###Step2
    HISATSUMMARY=str(SRR)+'.summary'
    HISATSAM=str(SRR)+'.sam'
    cmd='hisat2 -x '+str(SILVA)+' -1 '+str(read1)+' -2 '+str(read2)+' -p '+str(CPU)+' --summary-file '+str(HISATSUMMARY)+' --no-unal --no-hd -S '+str(HISATSAM)
    logging.info('Aligning reads against '+str(SILVA)+" by hisat2\n")
    os.system(cmd)
    #cmd="rm -f "+str(read1)+" "+str(read2)
    #os.system(cmd)
    ###Step3
    Genus={}
    with open(TaxB,"r") as infile:
        for line in infile:
            tax=line.strip()
            ID=tax.strip().split("\t")[0]
            Tax=tax.strip().split("\t")[2]
            if Tax=='family':
                IDS=ID.strip().split(";")
                gID=IDS[-2]
                fID=IDS[-3]
                if gID!='uncultured':
                    Genus[gID]=fID
    LINKG={}
    with open(RefID,"r") as infile:
        for line in infile:
            tax=line.strip()
            ID=tax.strip().split("\t")[0]
            Tax=tax.strip().split("\t")[1]
            Taxs=Tax.strip().split(";")
            if 'Chloroplast' in Tax:
                LINKG[ID]='Chloroplast'
            elif 'Mitochondria' in Tax:
                LINKG[ID]='Mitochondria'
            else:
                if len(Taxs)>2:
                    for i in range(-3,1,1):
                        R=Taxs[i]
                        if Genus.get(R)!=None:
                            LINKG[ID]=R
                if len(Taxs)==2:
                    for i in range(-2,1,1):
                        R=Taxs[i]
                        if Genus.get(R)!=None:
                            LINKG[ID]=R
    READS=[]
    REFS=[]
    NRC={}
    MAPS=[]
    X=-1
    Y=-1
    with open(HISATSAM,"r") as infile:
        for line in infile:
            gff=line.strip()
            ID=gff.strip().split("\t")[0]
            ID1=ID.strip().split(".")[0]
            ID2=ID.strip().split(".")[1]
            ID3=ID.strip().split(".")[2]
            ID12=str(ID1)+"."+str(ID2)
            if NRC.get(ID12)==None:
                X=X+1
                NRC[ID12]=X
                READS.append(ID12)
            
            REF=gff.strip().split("\t")[2]
            if NRC.get(REF)==None:
                Y=Y+1
                NRC[REF]=Y
                REFS.append(REF)
        
            AM=gff.strip().split("\t")[5]
            MAP=str(ID12)+"\t"+str(REF)+"\t"+str(AM)+"\t"+str(ID3)
            MAPS.append(MAP)

    Z=len(MAPS)
    print(X,Y,Z)
    ###Step4
    Y=Y+1
    X=X+1
    arrayXYZ=np.full((Y,X,6),'XXXXXXXX.XXXXXX.XXXXXX')
    MapNumber=0
    for MAP in MAPS:
        MapNumber=MapNumber+1
        progress_bar(MapNumber, Z)
        ID=MAP.strip().split("\t")[0]
        REF=MAP.strip().split("\t")[1]
        P=MAP.strip().split("\t")[-1]
        MS=MAP.strip().split("\t")[2]
        X=NRC[ID]
        Y=NRC[REF]
        if LINKG.get(REF)!=None:
            G=LINKG[REF]
            #print(REF,G)
            if int(P)==1:
                arrayXYZ[Y,X,0]=str(G)
                arrayXYZ[Y,X,2]=str(REF)
                arrayXYZ[Y,X,4]=str(ID)
            if int(P)==2:
                arrayXYZ[Y,X,1]=str(G)
                arrayXYZ[Y,X,3]=str(REF)
                arrayXYZ[Y,X,5]=str(ID)


    RDC=str(SRR)+'.read.class1'
    fp = open(RDC, "w")
    outfile="Read\tNum\tFamilies\tRefGenes"
    print(outfile,file=fp)
    print("\nstep4\n")
    FAMILIES=[]
    READN={}
    for x in range(0,X):
        progress_bar(x,X)
        Read=READS[x]
        GENUS=np.unique(arrayXYZ[:,x,0:1])
        GENES=np.unique(arrayXYZ[:,x,2:3])
        GLS=[]
        if 'Chloroplast' not in GENUS and 'Mitochondria' not in GENUS:
            for z in GENUS:
                if z!='XXXXXXXX.XXXXXX.XXXXXX':
                    GLS.append(z)
                    FAMILIES.append(z)
            FAMILIES=deleteDuplicatedElement(FAMILIES)
        if 'Chloroplast' not in GENES and 'Mitochondria' not in GENES:        
            REFG=[]
            for z in GENES:
                if z!='XXXXXXXX.XXXXXX.XXXXXX':
                    REFG.append(z)
    
        num=len(GLS)
        if int(num)>0:
            READN[Read]=int(num)
            out=str(Read)+"\t"+str(num)+"\t"+str(GLS)+"\t"+str(REFG)
            print(out,file=fp)
    fp.close()

    print("\nclass2\n")

    RDC=str(SRR)+'.read.class2'
    fp = open(RDC, "w")
    outfile="Family\tRefGenes\tNum\tReads"
    print(outfile,file=fp)
    R=len(FAMILIES)
    rnum=0
    for f in FAMILIES:
        rnum=int(rnum)+1
        progress_bar(rnum,R)
        UNR=[]
        GENES=[]
        for gene in REFS:
            if LINKG.get(gene)!=None and NRC.get(gene)!=None:
                Family=LINKG[gene]
                y=NRC[gene]
                tnum=0
                if f==Family:
                    READS=np.unique(arrayXYZ[y,:,4:5])
                    for r in READS:
                        if r!='XXXXXXXX.XXXXXX.XXXXXX' and READN.get(r)!=None:
                            RN=READN[r]
                            #print(RN)
                            if int(RN)==1:
                                UNR.append(r)
                                tnum=1
                if int(tnum)>0:
                    GENES.append(gene)
        UNRN=len(UNR)
        if int(UNRN)>0:
            out=str(f)+"\t"+str(GENES)+"\t"+str(UNRN)+"\t"+str(UNR)
            print(out,file=fp)
    fp.close()

    cmd="tar -czvf "+str(HISATSAM)+".tgz "+str(HISATSAM)
    os.system(cmd)
    #cmd="rm -f "+str(HISATSAM)
    #os.system(cmd)
    
    #logging.info("Start sorting results..")