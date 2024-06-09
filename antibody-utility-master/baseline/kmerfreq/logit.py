import string, itertools, cPickle, argparse, numpy as np, h5py
from os.path import join
from sklearn.linear_model import LogisticRegressionCV

def parse_args():
    parser = argparse.ArgumentParser(description="help script")
    parser.add_argument("--datadir", type=str)
    parser.add_argument("--n_jobs", type=int, default=16)
    return parser.parse_args()

args = parse_args()

with open(join(args.datadir, 'train.kmerfreq.pkl'), 'rb') as f:
    train_kmer = cPickle.load(f)

with open(join(args.datadir, 'test.kmerfreq.pkl'), 'rb') as f:
    test_kmer = cPickle.load(f)

with open(join(args.datadir, 'train.label')) as f:
    train_label = [np.argmax(map(int, x.split())) for x in f]

model = LogisticRegressionCV(n_jobs=args.n_jobs)
model.fit(train_kmer, train_label)

comp_kwargs = {'compression': 'gzip', 'compression_opts': 1}
with h5py.File(join(args.datadir, 'pred.test.logit.h5'), 'w') as f:
    f.create_dataset('pred', data=model.predict_proba(test_kmer), **comp_kwargs)

