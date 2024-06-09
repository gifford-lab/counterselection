from collections import defaultdict
from os.path import join, exists
from os import makedirs
import sys

seqfile = sys.argv[1]
outdir = sys.argv[2]

if not exists(outdir):
    makedirs(outdir)

seq = defaultdict(list)
with open(seqfile) as f:
    for x in f:
        s = x.split()
        if len(s) > 0:
            s = s[0]
            seq[len(s)].append(s)

for l in seq.keys():
    with open(join(outdir, 'len'+str(l)), 'w') as f:
        for x in seq[l]:
            f.write('{}\n'.format(x))
