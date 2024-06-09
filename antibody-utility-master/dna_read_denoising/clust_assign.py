import Levenshtein as lev, h5py, multiprocessing as mp, argparse, distance
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='featurefile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-s', dest='seqfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-o', dest='outfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-rc', dest='rho_cutoff', required=True, type=float, help='the length of the sequences')
    parser.add_argument('-dc', dest='delta_cutoff', required=True, type=float, help='the length of the sequences')
    parser.add_argument('-j', dest='njobs', default=16, type=int, help='the length of the sequences')
    return parser.parse_args()

args = parse_args()

#################################
feat = pd.read_csv(args.featurefile, sep='\t')

with open(args.seqfile) as f:
    seq = [x.split()[0] for x in f]

print 'find the centers'
center_seq = [ s for idx, s in enumerate(seq) if feat['rho'][idx] > args.rho_cutoff and feat['delta'][idx] > args.delta_cutoff]
assert(len(center_seq)>0)

assign = dict()
clust = dict()
for idx, s in enumerate(center_seq):
    assign[s] = idx
    clust[idx] = [s]


################################
def find_center(seq, centers):
    best = -1
    for c  in centers:
        t_d = distance.hamming(seq, c)
        if best== -1 or t_d < best:
            best = t_d
            out = c
    return out

def slave(args):
    s = args
    return s, find_center(s, center_seq)

print 'assign the rest'
slave_args = [s for s in seq if not (s in assign)]

pool = mp.Pool(processes=args.njobs)
result = pool.map(slave, slave_args)
pool.close()
pool.join()

for s, center in result:
    assign[s] = assign[center]
    clust[assign[center]].append(s)

###############################
with open(args.outfile+'.assign', 'w') as f:
    for s in seq:
        f.write('{}\t{}\n'.format(s, assign[s]))

with open(args.outfile+'.clust', 'w') as f:
    for c in clust.keys():
        f.write('{}\t{}\n'.format(c, '\t'.join(clust[c])))
