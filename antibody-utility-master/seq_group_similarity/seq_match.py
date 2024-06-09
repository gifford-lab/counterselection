import sys,Levenshtein as lev,collections,argparse,pandas as pd,numpy as np, multiprocessing as mp
from os.path import join,dirname,basename,exists
from os import system,makedirs

def mindist(targetset, mystr, dist):
    alldist = [dist(x, mystr) for x in targetset]
    argmin = np.argmin(alldist)
    return [targetset[argmin],alldist[argmin]]

def exact_dist(str1, str2):
    return lev.distance(str1, str2)

def shift_dist(str1, str2):
    mstr1,mstr2 = (str1,str2) if len(str1) > len(str2) else (str2,str1)
    l1,l2 = len(mstr1),len(mstr2)
    return min([lev.distance(mstr1[idx:(idx+l2)], mstr2) for idx in range(l1-l2+1)])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tsv1',type=str, help='a tsv file of sequences each of which will be compared against another group of sequences and calculate the min distance')
    parser.add_argument('--tsv2',type=str, help='another tsv file of sequences to compare against')
    parser.add_argument('--mode',type=str, help="'exact' or 'shift' for exact matching or shift matching")
    parser.add_argument('--outputfile',type=str, help="the file to save the matching results")
    parser.add_argument('--jobs',type=int, default=16, help="num of jobs to process in parallel")
    parser.add_argument('--strip',type=str, default='', help="padding to remove")
    return parser.parse_args()

def slave(seq2compare):
    return mindist(seqs[tsv2], seq2compare, mydist)

args = parse_args()
tsv1, tsv2, mode, outputfile = args.tsv1, args.tsv2, args.mode, args.outputfile

### Load data
seqs = collections.defaultdict(list)
for tsv in [tsv1, tsv2]:
    with open(tsv) as f:
        seqs[tsv] = [x.split()[1].strip(args.strip) for x in f]

### Matching
mydist = exact_dist if mode == 'exact' else shift_dist

pool = mp.Pool(processes=args.jobs)
result = pool.map(slave, seqs[tsv1])
pool.close()
pool.join()

dist = pd.DataFrame([[x] + result[idx] for idx, x in enumerate(seqs[tsv1])], columns=['seq', 'closest_target', 'mindist'])

### Output
if not exists(dirname(outputfile)):
    makedirs(dirname(outputfile))
dist.sort_values('mindist').to_csv(outputfile,sep='\t')
