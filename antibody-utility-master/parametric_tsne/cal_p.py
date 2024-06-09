import Levenshtein as lev, numpy as np, h5py, sys
import multiprocessing as mp, argparse

def Hbeta(D, beta):
    P = np.exp(-D * beta)
    sumP = np.sum(P)
    H = np.log(sumP) + beta * np.sum(np.multiply(D, P)) / sumP
    P = P / sumP
    return H, P

def x2p(X, u=15, tol=1e-4, print_iter=500, max_tries=50, verbose=0):
    # Initialize some variables
    n = X.shape[0]                     # number of instances
    P = np.zeros((n, n))               # empty probability matrix
    beta = np.ones(n)                  # empty precision vector
    logU = np.log(u)                   # log of perplexity (= entropy)

    # Compute pairwise distances
    if verbose > 0: print('Computing pairwise distances...')
    D = np.zeros((n, n))
    for i in range(n-1):
        for j in range(i+1, n):
            D[i, j] = np.power(lev.distance(X[i], X[j]), 2)
            D[j, i] = D[i, j]
    #sum_X = np.sum(np.square(X), axis=1)
    # note: translating sum_X' from matlab to numpy means using reshape to add a dimension
    #D = sum_X + sum_X[:,None] + -2 * X.dot(X.T)

    # Run over all datapoints
    if verbose > 0: print('Computing P-values...')
    for i in range(n):

        if verbose > 1 and print_iter and i % print_iter == 0:
            print('Computed P-values {} of {} datapoints...'.format(i, n))

        # Set minimum and maximum values for precision
        betamin = float('-inf')
        betamax = float('+inf')

        # Compute the Gaussian kernel and entropy for the current precision
        indices = np.concatenate((np.arange(0, i), np.arange(i + 1, n)))
        Di = D[i, indices]
        H, thisP = Hbeta(Di, beta[i])

        # Evaluate whether the perplexity is within tolerance
        Hdiff = H - logU
        tries = 0
        while abs(Hdiff) > tol and tries < max_tries:

            # If not, increase or decrease precision
            if Hdiff > 0:
                betamin = beta[i]
                if np.isinf(betamax):
                    beta[i] *= 2
                else:
                    beta[i] = (beta[i] + betamax) / 2
            else:
                betamax = beta[i]
                if np.isinf(betamin):
                    beta[i] /= 2
                else:
                    beta[i] = (beta[i] + betamin) / 2

            # Recompute the values
            H, thisP = Hbeta(Di, beta[i])
            Hdiff = H - logU
            tries += 1

        # Set the final row of P
        P[i, indices] = thisP

    if verbose > 0:
        print('Mean value of sigma: {}'.format(np.mean(np.sqrt(1 / beta))))
        print('Minimum value of sigma: {}'.format(np.min(np.sqrt(1 / beta))))
        print('Maximum value of sigma: {}'.format(np.max(np.sqrt(1 / beta))))

    return P, beta

def compute_joint_probabilities(samples, outfile_prefix, batch_size=5000, perplexity=30, tol=1e-5, verbose=0, n_batch2output=10, n_jobs=16):

    # Initialize some variables
    n = samples.shape[0]
    print 'num of samples', n
    batch_size = min(batch_size, n)

    # Precompute joint probabilities for all batches
    if verbose > 0: print('Precomputing P-values...')

    sample_max = n // batch_size * batch_size
    num2output = batch_size * n_batch2output
    samples_split = [
            (samples[i:(i+min(num2output, sample_max-i))],
                i // num2output + 1,
                batch_size,
                perplexity,
                tol,
                verbose,
                outfile_prefix) for i in range(0, sample_max, num2output)]

    print 'batch size is', batch_size
    print 'num of batches to process', sample_max // batch_size
    print 'num of jobs', len(samples_split)

    pool = mp.Pool(processes=n_jobs)
    pool.map(compute_worker, samples_split)
    pool.close()
    pool.join()

def compute_worker(args):
    samples, out_batch_cnt, batch_size, perplexity, tol, verbose, outfile_prefix = args

    n_batch2output = len(samples) // batch_size

    P = np.zeros((n_batch2output, batch_size, batch_size))

    for i in range(n_batch2output):
        curX = samples[(i*batch_size):((i+1)*batch_size)]                   # select batch
        p_, beta = x2p(curX, perplexity, tol, verbose=verbose) # compute affinities using fixed perplexity
        p_[np.isnan(p_)] = 0                                 # make sure we don't have NaN's
        p_ = (p_ + p_.T) # / 2                             # make symmetric
        p_ = p_ / p_.sum()                                 # obtain estimation of joint probabilities
        P[i] = np.maximum(p_, np.finfo(p_.dtype).eps)


    dump2file(P, samples, outfile_prefix, out_batch_cnt, batch_size)

def embed(seq, mapper, worddim):
    seq = list(seq) + [padding]*(args.outlen-len(seq))
    mat = np.asarray([mapper[element] if element in mapper else np.random.rand(worddim)*2-1 for element in seq]).transpose()
    return np.expand_dims(mat, axis=1)

def dump2file(P, samples, outfile, out_batch_cnt, batch_size):
    n_batch = len(P)
    y_out = P.reshape(batch_size * n_batch, -1)
    x_out = np.asarray([embed(seq, mapper, worddim) for seq in samples])

    comp_kwargs = {'compression': 'gzip', 'compression_opts': 1}
    with h5py.File(outfile+'.h5.batch'+str(out_batch_cnt), 'w') as f:
        f.create_dataset('data', data=x_out, **comp_kwargs)
        f.create_dataset('label', data=y_out, **comp_kwargs)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seqfile', dest='seqfile', type=str)
    parser.add_argument('--outfile', dest='outfile', type=str)
    parser.add_argument('--mode', dest='mode', type=str)
    parser.add_argument('--outlen', dest='outlen', type=int)
    parser.add_argument('--bs', dest='batchsize', type=int)
    parser.add_argument('--nb_per_outfile', dest='nb_per_outfile', type=int, default=10)
    parser.add_argument('--verbose', dest='verbose', type=int, default=1)
    return parser.parse_args()

args = parse_args()
if args.mode == 'dna':
    mapper = {'A':[1,0,0,0],'C':[0,1,0,0],'G':[0,0,1,0],'T':[0,0,0,1],'N':[0,0,0,0]}
    worddim = 4
    padding = 'N'
elif args.mode == 'aa':
    aa = 'RHKDESTNQCGPAVILMFYW'
    padding = 'J'
    worddim = len(aa)
    mapper = dict()
    for idx, x in enumerate(list(aa)):
        t = [0] * worddim
        t[idx] = 1
        mapper[x] = t
    mapper['J'] = [0] * worddim

with open(args.seqfile) as f:
    compute_joint_probabilities(np.asarray([x.strip() for x in f]), args.outfile, batch_size=args.batchsize, n_batch2output=args.nb_per_outfile, verbose=args.verbose)
