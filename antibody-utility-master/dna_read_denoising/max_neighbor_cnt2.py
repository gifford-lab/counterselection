import Levenshtein as lev, h5py, multiprocessing as mp, argparse, pandas as pd
from os.path import join, exists, dirname
from os import makedirs
from itertools import izip
import numpy as np
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='indir', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-s', dest='seqfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-r', dest='readfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-dc', default=2, type=int, help='the length of the sequences')
    parser.add_argument('-j', dest='njobs', default=16, type=int, help='the length of the sequences')
    return parser.parse_args()


args = parse_args()

#######################
slave_args = []
bs_cnt = 0
while exists(join(args.indir, 'batch'+str(bs_cnt))):
    slave_args.append(join(args.indir, 'batch'+str(bs_cnt)))
    bs_cnt += 1

assert(bs_cnt>0)

print 'get the counts'
cnt = defaultdict(int)

with open(args.readfile) as f:
    for x in f:
        cnt[x.strip()] += 1

with open(args.seqfile) as f:
    cnt_vec = np.asarray([cnt[x.strip()] for x in f])

print 'calculating neighbor cnt'

def slave_rho(args):
    datafile = args
    with open(datafile) as f:
        out = []
        for x in f:
            t_dist = np.asarray(x.split(), dtype=float)
            t_out = []
            for d in distance2cal:
                cnt_neighbor = cnt_vec[t_dist==d]
                max_neighbor = 0 if len(cnt_neighbor) == 0 else max(cnt_neighbor)
                t_out.append(max_neighbor)
            out.append(t_out)
        return out

distance2cal = [i for i in range(1, args.dc)]
#result = np.asarray([slave_rho(args) for args in slave_args])
#max_neighbor_count = [item for sublist in result for item in sublist]
pool = mp.Pool(processes=args.njobs)
max_neighbor_count = np.asarray([item for sublist in pool.map(slave_rho, slave_args) for item in sublist])
pool.close()
pool.join()

print 'max_neighbor_count shape:', max_neighbor_count.shape


#######################
print 'outputing'
if not exists(dirname(args.outfile)):
    makedirs(dirname(args.outfile))

df = pd.DataFrame()
max_neighbor_count = max_neighbor_count.transpose()
for idx, d in enumerate(distance2cal):
    df['max_neighbor_cnt_d'+str(d)] = max_neighbor_count[idx]
df.to_csv(args.outfile, sep='\t', index=False)
