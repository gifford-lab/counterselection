import Levenshtein as lev, h5py, multiprocessing as mp, argparse, pandas as pd
from os.path import join, exists, dirname
from os import makedirs
from itertools import izip
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='indir', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-dc', required=True, type=float, help='the length of the sequences')
    parser.add_argument('-j', dest='njobs', default=16, type=int, help='the length of the sequences')
    parser.add_argument('-bs', required=True, type=int, help='the length of the sequences')
    return parser.parse_args()


args = parse_args()

#######################
slave_args = []
bs_cnt = 0
while exists(join(args.indir, 'batch'+str(bs_cnt))):
    slave_args.append(join(args.indir, 'batch'+str(bs_cnt)))
    bs_cnt += 1

assert(bs_cnt>0)

print 'calculating rho'

def slave_rho(args):
    datafile = args
    with open(datafile) as f:
        return [np.sum(np.asarray(x.split(), dtype=float) < dc) for x in f]

dc = args.dc
assert(dc>0)
pool = mp.Pool(processes=args.njobs)
rho = [item for sublist in pool.map(slave_rho, slave_args) for item in sublist]
pool.close()
pool.join()

#########################
print 'calculating delta'

def slave_delta(args):
    datafile, batch_offset = args[:]
    delta = []
    with open(datafile) as f:
        for idx, x in enumerate(f):
            t_dist = np.asarray(x.split(), dtype=float)
            rho_cutoff = rho[idx+batch_offset]
            better_center = np.where(rho>rho_cutoff)[0] # global index, not just this batch
            if len(better_center)==0:
                delta.append(max(t_dist))
            else:
                delta.append(min(t_dist[better_center]))
    return delta

slave_args_delta = [ (x, idx*args.bs) for idx, x in enumerate(slave_args)]

pool = mp.Pool(processes=args.njobs)
delta = [item for sublist in pool.map(slave_delta, slave_args_delta) for item in sublist]
pool.close()
pool.join()

#######################
print 'outputing'
if not exists(dirname(args.outfile)):
    makedirs(dirname(args.outfile))

df = pd.DataFrame()
df['rho'] = rho
df['delta'] = delta
df.to_csv(args.outfile, sep='\t', index=False)
