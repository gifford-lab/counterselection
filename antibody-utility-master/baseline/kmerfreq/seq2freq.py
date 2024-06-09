import string, itertools, cPickle, argparse, multiprocessing as mp
from scipy import sparse

def parse_args():
    parser = argparse.ArgumentParser(description="help script")
    parser.add_argument("--infile", type=str)
    parser.add_argument("--outfile", type=str)
    parser.add_argument("--k", type=int, default=3)
    return parser.parse_args()

args = parse_args()

bases = list(string.ascii_uppercase)
for x in ['B', 'O', 'U', 'Z', 'X']:
    bases.remove(x)
    kmers = [''.join(p) for p in itertools.product(bases, repeat=args.k)]

row = []
col = []
data = []
with open(args.infile) as f:
    seqs = [x.split()[1] for x in f]

def slave(args):
    idx, kmers, seq = args
    col = []
    data = []
    for kidx, kmer in enumerate(kmers):
        count = seq.count(kmer)
        if count > 0:
            col.append(kidx)
            data.append(count)
    return (idx, col, data)


slave_args = [ (idx, kmers, seq)   for idx, seq in enumerate(seqs)]
pool = mp.Pool(processes=20)
result = pool.map(slave, slave_args)
pool.close()
pool.join()

row = []
col = []
data = []
for x in result:
    row += [x[0]] * len(x[1])
    col += x[1]
    data += x[2]

print 'Finished getting row, col and data'
sparse_mat = sparse.csr_matrix((data, (row, col)), shape=(len(seqs), len(kmers)))

print 'Dumping to file'
with open(args.outfile, 'wb') as f:
    cPickle.dump(sparse_mat, f)
