import sys, Levenshtein as lev,numpy as np, multiprocessing as mp,random,collections
from itertools import izip
from os.path import join, exists
from os import makedirs

def permute(mystr, num):
    new = list(mystr)
    for x in np.random.permutation(range(len(mystr)))[:num]:
        new_val = new[x]
        while new_val == new[x]:
            new_val = mydict[np.random.randint(len(mydict))]
        new[x] = new_val
    return ''.join(new)

def slave(args):
    trial, init, dist, outfolder = args[:]
    np.random.seed(random.SystemRandom().randint(0,10000000))
    new = []
    for _, x in init:
        t_dist_group = dist[len(x)]
        t_dist = t_dist_group[np.random.randint(len(t_dist_group))]
        new.append(permute(x, t_dist))

    with open(join(outfolder, str(trial)), 'w')as f:
        for idx,x in enumerate(new):
            f.write('%s\t%s\n' % (init[idx][0], x))


f1 = sys.argv[1] # A tsv file of seeds
f2 = sys.argv[2] # A tsv file of new sequences generated from each seed
trialnum = int(sys.argv[3]) # The number of times we run permutation
outfolder = sys.argv[4] # The directory to output the permutation result (one file for each trial).

# Load amini acid symbols
with open('/cluster/zeng/code/research/antibody_panning/sep12_2016/mappers/20_aa') as f:
    mydict = [x.strip() for x in f]

# Calculate the empirical distribution of the number of changes for each input length
dist = collections.defaultdict(list)
init = []
with open(f1) as i1, open(f2) as i2, open(join(outfolder, 'distance_summary'), 'w') as fout:
    for x, y in izip(i1, i2):
        seed_seq = x.split()[1]
        new_seq = y.split()[1]
        cur_dist = lev.distance(seed_seq, new_seq)
        dist[len(seed_seq)].append(cur_dist)
        fout.write('%s\n' % '\t'.join([seed_seq, new_seq, str(cur_dist)]))
        init.append(x.split())

# Permute each seed according to the change distribution
if not exists(outfolder):
    makedirs(outfolder)

args = [[trial, init, dist, outfolder] for trial in range(trialnum)]
pool = mp.Pool(processes=20)
pool.map(slave,args)
pool.close()
pool.join()
