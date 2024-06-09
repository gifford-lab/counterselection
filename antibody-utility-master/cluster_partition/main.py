from collections import defaultdict
import copy, numpy as np, argparse
from os.path import join, exists
from os import makedirs
import operator, time
from numpy.random import permutation


def match(candidate, target, tol):
    loc = 0
    stack = []
    n_cand = len(candidate)
    if sum([x[1] for x in candidate]) < target:
        return []
    cand_sorted = sorted(candidate, key=lambda x: x[1], reverse=True)
    t_target = target
    for x in cand_sorted:
        if x[1] > t_target/2:
            t_target -= x[1]
            candidate.remove(x)
            candidate.insert(0, x)

    start = time.time()
    while time.time() - start < 60:

        x = candidate[loc]

        # If adding the current candidate already brings us close to the target, we add it to the solution and return
        if np.abs(target - x[1]) <= tol:
            return stack + [[x, loc]]

        # Otherwise it means adding the current candidate alone won't work
        if x[1] < target and loc < n_cand - 1:
            # If the current candidate can fit and we have more candidates to check, we add it to the stack and move to its next
            stack.append([x, loc])
            loc += 1
            target -= x[1]
        else:
            # Otherwise, we give up the curren candidate
            if loc < n_cand - 1:
                # we move to the next candidate if there is one
                loc += 1
            elif stack:
                # otherwise, we roll back by popping the stack, restoring the target and moving on to its next candidate
                popped = stack.pop()
                loc = popped[1] + 1
                target += popped[0][1]
            else:
                # if the stack is already empty or full of all the candidates possible, there is no solution
                return []
    if time.time() - start > 60:
        print('Search times out (limit=60s)!')
    return []


def multimatch(group, dataset_size, idx, maxtol):
    out = []

    tol = 0
    while True:
        # Perform matching for the current target
        print('start match', 'target:', dataset_size[idx], 'tolerance:', tol)
        trial = match(group, dataset_size[idx], tol)

        # If we succeed
        if trial:
            print('match succeeded. Num of groups:', len(trial))

            # Identify the remaining candidates groups
            group_new = copy.deepcopy(group)
            for x in trial:
                group_new.remove(x[0])

            if idx <  len(dataset_size) -2:
                # If we have >=2 targets left, we keep iterating
                new_match = multimatch(group_new, dataset_size, idx+1, maxtol)

                # If the recursion succeeds, we return the solution
                if new_match:
                    out.append((idx, trial))
                    out += new_match
                    return out
                else:
                    print('recursion failed')
            elif idx == len(dataset_size) -2:
                # Otherwise we directly check if the sum of the remaining group is close to the last target
                # as we don't want to discard any group
                if np.abs(sum([x[1] for x in group_new]) - dataset_size[idx+1]) <= maxtol:
                    print('the remaining groups can meet the last target')
                    out.append((idx, trial))
                    out.append(((idx+1), [ [x, idx] for idx, x in enumerate(group_new)]))
                    return out
                else:
                    print('the remaining groups fail to meet the last target;roll back the last match')
        else:
            print('match failed; increase the tolerance for the current target')

        if tol == maxtol:
            print('maxtol reached ; roll back to last recursion!')
            return None

        tol = min(2*tol or 1, maxtol)
    return out

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputfile', type=str, help='')
    parser.add_argument('--outdir', dest='outdir', type=str, help='')
    parser.add_argument('--outfiles', dest='outfiles', type=str, help='')
    parser.add_argument('--ratios', dest='ratios', type=str, help='')
    parser.add_argument('--tolratio', dest='tol_ratio', type=str, help='')
    return parser.parse_args()

args = parse_args()

outfiles = args.outfiles.split('_')
dataset_ratio = map(float, args.ratios.split('_'))

# Read the clustering file
group2seq = defaultdict(list)
group2size = dict()
with open(args.inputfile) as f:
    f.readline()
    for x in f:
        seq, _, gp, size = x.split()
        group2seq[gp].append(seq)
        group2size[gp] = int(size)

# Prepare for matching
group_tuple = permutation([(x,y) for x,y in group2size.items()])
group_tuple = [(x, int(y)) for x,y in group_tuple]
total_seq_n = sum([x[1] for x in group_tuple])
dataset_size = [int(total_seq_n*x) for x in dataset_ratio[:-1]]
dataset_size += [total_seq_n - sum(dataset_size)]
tol_size =  int(float(args.tol_ratio) * total_seq_n)
print 'dataset size:', dataset_size, 'tolerance size:', tol_size

result = multimatch(group_tuple, dataset_size, 0, tol_size)

# Output
if not exists(args.outdir):
    makedirs(args.outdir)
for partition in result:
    idx, groups = partition
    with open(join(args.outdir, outfiles[idx]), 'w') as f:
        for x in partition[1]:
            for seq in group2seq[x[0][0]]:
                f.write(seq+'\n')

