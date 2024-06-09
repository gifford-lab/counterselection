import Levenshtein as lev, h5py, multiprocessing as mp, argparse, pandas as pd
from os.path import join, exists, dirname
from os import makedirs,listdir
from itertools import izip
import numpy as np
from collections import defaultdict
from scipy.stats import binom
from scipy.misc import comb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-rep1_dir', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-rep2_dir', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-dc', required=True, type=int, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    return parser.parse_args()


args = parse_args()

def load_prob(mydir):
    myprob = dict()
    for myfile in listdir(mydir):
        if '.probs.v2' in myfile:
            with open(join(mydir, myfile)) as f:
                for x in f:
                    line = x.split()
                    if '>' not in line[0]:
                        myprob[line[0]] = max(map(float, line[1:]))
    return myprob

myprob1 = load_prob(args.rep1_dir)
myprob2 = load_prob(args.rep2_dir)

allseq = set(myprob1.keys()).union(set(myprob2.keys()))

if not exists(dirname(args.outfile)):
    makedirs(dirname(args.outfile))

with open(args.outfile, 'w') as f:
    for seq in allseq:
        p1 = myprob1[seq] if seq in myprob1 else 1
        p2 = myprob2[seq] if seq in myprob2 else 1

        if p1*p2 <= 0.05/len(allseq):
            f.write('{}\t{}\t{}\t{}\n'.format(seq, p1, p2, p1*p2))
