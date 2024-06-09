#!/usr/bin/env python
# python find_CDR_seqs.py merged_12_domtbl_results.txt amplicons_6458_12_pept.fa
# for k in 02 03 04 07 08 09 10 11 12 13 15 16 17; do python find_CDR_seqs.py merged_${k}_domtbl_results.txt amplicons_6458_${k}_pept.fa > merged_${k}_sequences.txt; done
import sys, pandas,numpy as np, argparse
from collections import defaultdict
from Bio import SeqIO
import Levenshtein as lev, cPickle
from os.path import join

ENDING = ['GACTAC', 'GACGTC']
ENDING_LEN = len(ENDING[0])

def check_len_correct_tail(seq):
    return None if len(seq) %3 != 0 or len(seq)<=ENDING_LEN else seq

def checkGifford(seq, primer):
    return True if lev.hamming(seq, primer) <= 2 else False

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blastdict', type=str, help='')
    parser.add_argument('--header_len', type=int, help='')
    parser.add_argument('--fasta',  type=str, help='')
    return parser.parse_args()

args = parse_args()
with open(args.blastdict) as f:
    hits_head, hits_tail = cPickle.load(f)

header_len = args.header_len
names = set(hits_head.keys()) & set(hits_tail.keys())
print >>sys.stderr, "looking for %d reads now" % len(names)

count = 0
errcount=0
correct=0
fin = open(args.fasta)

if args.mixed:
    gifford_primer_loc, gifford_primer = args.mixed.split('_')
    # the number of bp between the end of the sequence and the gifford_primer
    # so end + gifford_primer_loc is the first bp of the primer (0-based)
    gifford_primer_loc = int(gifford_primer_loc)

gifford_cnt = 0
for record in SeqIO.parse(args.fasta, "fasta"):
    name = record.name
    seq = record.seq.tostring()

    count += 1
    if count % 10000 == 0:
        print >>sys.stderr, count
    if len(seq) <= 0:
        break

    if name in names:

        # print name, len(seq), hits.loc[name]
        head = hits_head[name]
	tail=hits_tail[name]

        start = int(head[1] + header_len - head[0]) # 0-based sequence start
        end = int(tail[1] - tail[0]) # 1-based sequence end. So seq[start:end] is the fdr

        # We locate the known ending di-amino-acid (DY or DV) and then identify the begining by making sure the length is a multiple of 3.
        # Here we extend the tail by 2 bp in case of blast matching noise
        cdr = check_len_correct_tail(seq[start:(end+ENDING_LEN)])
        if cdr:
            print "\n".join(['>'+name, cdr])
            correct +=1
	else:
	    #print >>sys.stderr, "wrong length!"
	    errcount+=1
fin.close()
print >>sys.stderr,('Num of seq processed', count, 'Num of success', correct, 'Num of failure', errcount, 'Num of gifford', gifford_cnt)
