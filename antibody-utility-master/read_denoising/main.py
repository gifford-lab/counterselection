import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, multiprocessing as mp
import argparse, numpy as np, cPickle, h5py, pandas as pd, seaborn as sns
from os.path import join, dirname, basename, exists
from os import makedirs, system
from skbayes.mixture_models.dpmixture import DPPMM

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='readcnt_file', type=str, help='a csv file of sequences and counts')
    parser.add_argument('-t', dest='n_trial', type=int, help='num of trials when performing model selection', default=10)
    parser.add_argument('--mc', dest='n_maxclust', type=int, help='the maximum num of clusters to try in model selection')
    parser.add_argument('-p', dest='paramfile', default='', type=str, help='a tab-delimited file that specifies the name of the rounds to denoise and its previous round')
    parser.add_argument('-o', dest='outdir', type=str, help='the output directory')
    parser.add_argument('--command', type=str, help='the command')
    parser.add_argument('--clust_n_file', type=str, default='', help='a tab-delimited file that specifies the num of clusters to use in denoising for each round of interest')
    return parser.parse_args()

def create_dir(mydir):
    if not exists(mydir):
        makedirs(mydir)

def save_args(mydir):
    if args.paramfile:
        system(' '.join(['cp', args.paramfile, join(mydir, 'paramfile')]))
    if args.clust_n_file:
        system(' '.join(['cp', args.clust_n_file, join(mydir, 'clust_n_file')]))
    with open(join(mydir, 'args'), 'w') as f:
        for k, v in vars(args).items():
            f.write('%s\t%s\n' % (k, str(v)))

def train(args):
    data, n_clust = args[:]
    return DPPMM(n_clust).fit(data)

args = parse_args()
readcnt = pd.read_csv(args.readcnt_file, index_col=0)
model_select_dir = join(args.outdir, 'model_select')
denoise_dir = join(args.outdir, 'denoise')
command = args.command.split(',')

if 'model_select' in command:
    assert(args.paramfile)
    with open(args.paramfile) as f:
        cur_round = []
        prev_round = []
        for x in f:
            line = x.split()
            cur_round.append(line[0])
            prev_round.append(line[1])

    # Sequentially process each of the experiments specified in the parameter file
    all_model_compare = {}
    all_model_objects = {}
    create_dir(model_select_dir)

    for analysis_idx in range(len(cur_round)):
        # Focus on sequences that appearred in either the previous round or the current round
        cur_round_name, prev_round_name = cur_round[analysis_idx], prev_round[analysis_idx]
        data = np.copy(readcnt[cur_round_name])
        data = data[np.bitwise_or(readcnt[prev_round_name]!=0,  data!=0)].reshape(-1, 1)

        # Try different number of mixtures and pick the one with the highest likelyhood
        compare = []
        model_best_trial = {}
        mp_args = []
        for n_clust in range(1, args.n_maxclust+1):
            # Train it n_trial times and use the model with the maximum likelihood
            for t in range(args.n_trial):
                mp_args.append([data, n_clust])

        pool = mp.Pool(processes=16)
        models = pool.map(train, mp_args)
        pool.close()
        pool.join()

        for n_clust in range(1, args.n_maxclust+1):
            model_score = []
            model_mean = []
            model_object = []
            for t in range(args.n_trial):
                t_model = models.pop(0)
                model_score.append(max(t_model.scores_))
                model_mean.append(t_model.means_)
                model_object.append(t_model)

            best_trial = np.argmax(model_score)
            compare.append([n_clust, model_score[best_trial], model_mean[best_trial]])
            model_best_trial[n_clust] = model_object[best_trial]

        # Save the analysis
        compare_pd = pd.DataFrame(compare, columns=['n_mix', 'score', 'means'])
        all_model_compare[cur_round_name] = compare_pd
        all_model_objects[cur_round_name] = model_best_trial
        plot = sns.factorplot(x='n_mix', y='score', data=compare_pd)
        plt.title(cur_round_name)
        plot.savefig(join(model_select_dir, cur_round_name)+'.png')

    with open(join(model_select_dir, 'allmodels.pkl'), 'w') as f:
        cPickle.dump([all_model_compare, all_model_objects], f)
    save_args(model_select_dir)

if 'denoise' in command:
    # Load the trained models and the hand-picked number of mixtures for each experiment
    with open(join(model_select_dir, 'allmodels.pkl')) as f:
        [all_model_compare, all_model_objects] = cPickle.load(f)

    cur_round = []
    assert(args.clust_n_file)
    with open(args.clust_n_file) as f:
        n_clust = dict()
        for x in f:
            line = x.split()
            n_clust[line[0]] = int(line[1])
            cur_round.append(line[0])

    # Sequentially denoise each experiment
    create_dir(denoise_dir)
    reads_denoised = pd.DataFrame()
    info2print = []

    for analysis_idx in range(len(cur_round)):
        cur_round_name = cur_round[analysis_idx]
        new_data = np.copy(readcnt[cur_round_name])

        # Assign each sequence to a cluster and identify the cluster with the lowest Poission parameter
        model = all_model_objects[cur_round_name][n_clust[cur_round_name]]
        clust = model.predict(new_data.reshape(-1,1))
        clust_unique = np.unique(clust)
        clust2kick = clust_unique[np.argmin(model.means_.squeeze()[clust_unique])]
        clust2kick_mean = model.means_.squeeze()[clust2kick]

        # Plot the sequences to remove and the sequences to keep
        sns.distplot(np.log(new_data[clust==clust2kick]+0.1), color='r')
        ax = sns.distplot(np.log(new_data[clust!=clust2kick]+0.1), color='g')
        plt.xlabel('readcnt')
        ax.get_figure().savefig(join(denoise_dir, cur_round_name+'.png'))

        # Clear the reads of sequences in the cluster to remove;
        # Deduct the reads of the other sequences by the Poission parameter of the cluster to remove.
        new_data[clust==clust2kick] = 0
        new_data = np.round(new_data - clust2kick_mean)
        new_data[new_data<0] = 0
        reads_denoised[cur_round_name] = new_data
        info2print.append([cur_round_name, model.means_.squeeze(), np.unique(clust), clust2kick, clust2kick_mean, np.count_nonzero(readcnt[cur_round_name]), np.count_nonzero(new_data)])

    reads_denoised.index = readcnt.index
    reads_denoised.to_csv(join(denoise_dir, 'denoised.csv'), index=True)
    pd.DataFrame(info2print, columns=['data', 'cluster_mean', 'cluster_assigned', 'cluster2kick', 'cluster2kick_mean', 'n_nonzero_bfr', 'n_nonzero_aft']).to_csv(join(denoise_dir, 'cluster_stats.tsv'), index=False)
    save_args(denoise_dir)


