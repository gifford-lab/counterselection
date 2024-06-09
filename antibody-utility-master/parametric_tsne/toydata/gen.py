import numpy as np
import random
import string

seeds = ['AAAAAAAA', 'GGGGGGGG']
n_change = 1
outdir = 'test_n1'

def gen(n_seq, outfile):
    seqs = set()
    for _ in range(n_seq):
        seq_idx = np.random.randint(2)
        flag = False
        while not flag:
            seq = list(seeds[seq_idx])
            for pos in np.random.randint(0, high=len(seeds[seq_idx]), size=n_change):
                seq[pos] = random.choice(string.ascii_uppercase)
            seq = ''.join(seq)
            if seq not in seqs:
                seqs.add(seq)
                flag = True

    with open(outfile, 'w') as f:
        for x in seqs:
            f.write('%s\n' % x)

gen(10000, outdir+'/train.seq')
gen(5000, outdir+'/valid.seq')
