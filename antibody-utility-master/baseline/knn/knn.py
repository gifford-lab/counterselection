from sklearn.neighbors import KNeighborsClassifier
from os.path import dirname,join,exists,basename,realpath,dirname
from sklearn.metrics import roc_auc_score,accuracy_score
from os import makedirs
import numpy as np,distance,argparse, h5py

cwd = dirname(realpath(__file__))
def parse_args():
    parser = argparse.ArgumentParser(description="help script")
    parser.add_argument("--topdir", type=str)
    parser.add_argument("--mapper", type=str, default='', dest='mapperfile')
    parser.add_argument("--nn", type=int, default=5, dest='nn')
    parser.add_argument("--outputfile", default='')
    parser.add_argument("--paddingtolen", default=-1, type=int)
    parser.add_argument("--padding", default="J")
    parser.add_argument("--pred_tsv", default='')
    parser.add_argument("--pred_label", default='')
    parser.add_argument("--njobs", default=10, type=int)
    return parser.parse_args()

args = parse_args()

with open(args.mapperfile) as f:
    d = [x.split() for x in f]

mydict = {}
for x in d:
    myvect = x[1:]
    mydict[x[0]] = x[1:].index('1') + 1 if '1' in myvect else 0

def repadding(seq):
    if args.paddingtolen != -1:
	core = [x for x in seq if x!= args.padding]
        core += [args.padding] * (args.paddingtolen - len(core))
    else:
	core = seq
    return [mydict[x] for x in core]


datafile = join(args.topdir, 'train.tsv')
labelfile = join(args.topdir, 'train.label')
with open(datafile) as f1,open(labelfile) as f2:
    train_data = np.asarray([ repadding(x.split()[1]) for x in f1])
    train_label = [ np.argmax(map(int, x.split())) for x in f2]

datafile = args.pred_tsv or join(args.topdir, 'test.tsv')
with open(datafile) as f1,open(labelfile) as f2:
    test_data = np.asarray([ repadding(x.split()[1]) for x in f1])

print 'Start training'
knn = KNeighborsClassifier(metric='hamming', n_jobs=args.njobs, n_neighbors=args.nn).fit(train_data, train_label)

print 'Start predicting on the test set'
comp_kwargs = {'compression': 'gzip', 'compression_opts': 1}
with h5py.File(join(args.topdir, 'pred.test.knn-'+str(args.nn)+'.h5'), 'w') as f:
    f.create_dataset('pred', data=knn.predict_proba(test_data), **comp_kwargs)
