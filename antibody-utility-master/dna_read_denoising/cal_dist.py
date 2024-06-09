import Levenshtein as lev, h5py, multiprocessing as mp, argparse, distance
from os.path import join, exists
from os import makedirs

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
        f.write('\t'.join([str(distance.hamming(x, s)) for s in seq])+ '\n')

