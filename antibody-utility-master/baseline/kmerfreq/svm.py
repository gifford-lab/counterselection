import string, itertools, cPickle, argparse, numpy as np, h5py
from os.path import join
from sklearn.svm import SVC

def parse_args():
    parser = argparse.ArgumentParser(description="help script")
    parser.add_argument("--datadir", type=str)
    return parser.parse_args()

args = parse_args()

with open(join(args.datadir, 'train.kmerfreq.pkl'), 'rb') as f:
    train_kmer = cPickle.load(f)

with open(join(args.datadir, 'test.kmerfreq.pkl'), 'rb') as f:
    test_kmer = cPickle.load(f)

with open(join(args.datadir, 'train.label')) as f:
    train_label = [np.argmax(map(int, x.split())) for x in f]

rf = SVC()
rf.fit(train_kmer, train_label)

comp_kwargs = {'compression': 'gzip', 'compression_opts': 1}
with h5py.File(join(args.datadir, 'pred.test.svm.h5'), 'w') as f:
    f.create_dataset('pred', data=rf.predict_proba(test_kmer), **comp_kwargs)

