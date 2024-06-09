import Levenshtein as lev, h5py, multiprocessing as mp, argparse, pandas as pd
from os.path import join, exists, dirname
from os import makedirs
from itertools import izip
import numpy as np
from collections import defaultdict
from scipy.stats import binom
from scipy.misc import comb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='featurefile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-s', dest='seqfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-r', dest='readfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-dc', required=True, type=int, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    return parser.parse_args()


args = parse_args()

#######################

print 'get the counts'
cnt = defaultdict(int)

with open(args.readfile) as f:
    for x in f:
        cnt[x.strip()] += 1

########################

print 'get the max neighbor cnt'
feat = pd.read_csv(args.featurefile, sep='\t')

#######################
print 'determine noise sequences'

with open(args.seqfile) as f:
    seq = [x.strip() for x in f]
    seqlen = [len(x) for x in seq]

def prob(e, L, N, k, M):
    if N==0:
        return 0
    p = e**k * (1-e)**(L-k)
    return 1-binom.cdf(M-1, M+N, p)**comb(L, k)

distance = np.asarray([i for i in range(1,args.dc)])
e = 0.001

seqidx = 0
center_seq = []
n_uniq_seq = len(cnt.keys())
#multi_real = 0
probs = []
for item, row in feat.iterrows():
    keep = True
    #keep_cnt = 0
    t_cnt = cnt[seq[seqidx]]
    t_len = seqlen[seqidx]
    t_prob_list = []
    for didx, d in enumerate(distance):
        t_prob = prob(e, t_len, float(row['max_neighbor_cnt_d'+str(d)]), d, t_cnt)
        t_prob_list.append(t_prob)
        if t_prob>=0.05/n_uniq_seq:
            keep = False
            #keep_cnt += 1
            #break
    probs.append([seq[seqidx]] + t_prob_list)
    if keep:
        center_seq.append(seq[seqidx])
    #if keep_cnt >1:
    #    multi_real +=1
    seqidx += 1

#print 'multi_real:', multi_real

with open(args.outfile+'.centers', 'w') as f:
    for c in center_seq:
        f.write('{}\n'.format(c))

with open(args.outfile+'.probs', 'w') as f:
    for prob in probs:
        f.write('{}\n'.format('\t'.join(map(str, prob))))
