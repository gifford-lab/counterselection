import Levenshtein as lev, h5py, multiprocessing as mp, argparse, distance
from os.path import join, exists
from os import makedirs
import numpy as np
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='seqfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-t', dest='trunkfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-bs', dest='batchsize', default=5000, type=int, help='the length of the sequences')
    return parser.parse_args()

args = parse_args()

with open(args.seqfile) as f:
    seq = [x.split()[0] for x in f]

with open(args.trunkfile) as f:
    trunk = [x.split()[0] for x in f]

with open(args.outfile, 'w') as f:
    for x in trunk:
        mydict = defaultdict(list)
        for s_idx, s in enumerate(seq):
            t_dist = distance.hamming(x, s)
            if t_dist <= 3:
                mydict[t_dist].append(str(s_idx))
        f.write('{}\t{}\t{}\n'.format('dist1:'+','.join(mydict[1]), 'dist2:'+','.join(mydict[2]), 'dist3:'+','.join(mydict[3])))

