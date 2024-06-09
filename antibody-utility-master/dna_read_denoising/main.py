from os.path import join, exists
from os import system, listdir, makedirs
import argparse, numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='outdir', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-s', dest='seqfile', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-c', dest='order', required=True, type=str, help='the length of the sequences')
    parser.add_argument('-j', dest='njobs', default=16, type=int, help='the length of the sequences')
    parser.add_argument('-dc', default=-1, type=int, help='the length of the sequences')
    parser.add_argument('-nc', dest='neighbor_cutoff', default=2.0, type=float, help='the length of the sequences')
    parser.add_argument('-bs', default=5000, type=float, help='the length of the sequences')
    parser.add_argument('-nt', default=-1, type=int, help='the length of the sequences')
    parser.add_argument('-replist', default=None, type=str, help='the length of the sequences')
    return parser.parse_args()

args = parse_args()

split_dir =  join(args.outdir, 'split_len')
dist_prep_dir =  join(args.outdir, 'dist_prep')
dist_dir = join(args.outdir, 'dist')
nb_dir = join(args.outdir, 'nb')
feat_dir = join(args.outdir, 'feat')
clust_dir = join(args.outdir, 'clust')
sgelog = join(args.outdir, 'sgelog')
clust_cutoff_file = join(args.outdir, 'delta_cutoff')
maxneighborcnt_dir = join(args.outdir, 'max_neighbor_dc'+str(args.dc))
maxneighbor_clust_dir = join(args.outdir, 'maxneighbor_clust_dc'+str(args.dc)+'_ratio'+str(args.neighbor_cutoff))

def create_dir(outdir):
    if not exists(outdir):
        makedirs(outdir)

create_dir(args.outdir)

if args.order == 'uniq':
    system(' '.join(['awk \'NR % 2 == 0\'', args.seqfile, '| sort | uniq', '>', join(args.outdir, 'uniq.seq')]))

if args.order == 'split':
    cmd = ' '.join(['python split_by_len.py', join(args.outdir, 'uniq.seq'), join(args.outdir, 'split_len')])
    system(cmd)

if args.order == 'prep_dist':

    def split_in_trunk(seq, trunk=5000):
        return [seq[i:min(i+trunk, len(seq))]  for i in range(0, len(seq), trunk)]

    for filename in listdir(split_dir):
	with open(join(split_dir, filename)) as f:
	    seq = [x.split()[0] for x in f]

        create_dir(join(dist_prep_dir, filename))
	for idx, trunk in enumerate(split_in_trunk(seq, trunk=args.bs)):
	    with open(join(dist_prep_dir, filename, 'batch'+str(idx)), 'w') as f:
	        for s in trunk:
	            f.write(s+'\n')

if args.order == 'dist':
    create_dir(sgelog)
    allfiles = listdir(split_dir)
    allfiles_int = np.asarray([int(x.split('len')[1]) for x in allfiles])
    allfiles = np.asarray(allfiles)[np.argsort(-allfiles_int)]
    for filename in allfiles:
        create_dir(join(dist_dir, filename))
        for trunk in listdir(join(dist_prep_dir, filename)):
            cmd = ' '.join(['python cal_dist.py',
                '-s', join(split_dir, filename),
                '-t', join(dist_prep_dir, filename, trunk),
                '-o', join(dist_dir, filename, trunk),
                '-bs', str(args.bs),
                ])
            print cmd
            system('echo  \"{}"| /usr/bin/qsub -e {} -o {} -N {} -wd `pwd`'.format(cmd, sgelog, sgelog, filename+'.'+trunk))



if args.order == 'find_nb':
    create_dir(sgelog)
    allfiles = listdir(split_dir)
    allfiles_int = np.asarray([int(x.split('len')[1]) for x in allfiles])
    allfiles = np.asarray(allfiles)[np.argsort(-allfiles_int)]
    for filename in allfiles:
        create_dir(join(nb_dir, filename))
        for trunk in listdir(join(dist_prep_dir, filename)):
            cmd = ' '.join(['python find_nb.py',
                '-s', join(split_dir, filename),
                '-t', join(dist_prep_dir, filename, trunk),
                '-o', join(nb_dir, filename, trunk),
                '-bs', str(args.bs),
                ])
            print cmd
            system('echo  \"{}"| /usr/bin/qsub -e {} -o {} -N {} -wd `pwd`'.format(cmd, sgelog, sgelog, filename+'.'+trunk))

if args.order == 'find_nb_single':
    create_dir(sgelog)
    allfiles = listdir(split_dir)
    allfiles_int = np.asarray([int(x.split('len')[1]) for x in allfiles])
    allfiles = np.asarray(allfiles)[np.argsort(-allfiles_int)]
    runscript = 'torun'
    with open(runscript, 'w') as f:
        cnt = 0
        for filename in allfiles:
            create_dir(join(nb_dir, filename))
            for trunk in listdir(join(dist_prep_dir, filename)):
                cmd = ' '.join(['python find_nb.py',
                    '-s', join(split_dir, filename),
                    '-t', join(dist_prep_dir, filename, trunk),
                    '-o', join(nb_dir, filename, trunk),
                    '-bs', str(args.bs),
                    ])
                f.write(cmd+'\n')
                cnt += 1

    print('num of jobs to run:', cnt)
    system(' '.join(['cat {} | parallel '.format(runscript)]))
    system(' '.join(['touch {}'.format(nb_dir+'.done')]))


if args.order == 'feat':
    assert(args.dc>0)
    create_dir(feat_dir)
    for filename in listdir(split_dir):
        cmd = ' '.join(['python cal_feat.py',
            '-i', join(dist_dir, filename),
            '-o', join(feat_dir, filename),
            '-dc', str(args.dc),
            '-j', str(args.njobs),
            '-bs', str(args.bs),
            ])
        print cmd
        system(cmd)


if args.order == 'max_neighbor_cnt2':
    assert(args.dc>0)
    t_outdir = maxneighborcnt_dir + '_perdist'
    create_dir(t_outdir)
    for filename in listdir(split_dir):
        cmd = ' '.join(['python max_neighbor_cnt2.py',
            '-i', join(dist_dir, filename),
            '-r', args.seqfile,
            '-s', join(split_dir, filename),
            '-o', join(t_outdir, filename),
            '-dc', str(args.dc),
            '-j', str(args.njobs),
            ])
        print cmd
        system(cmd)


if args.order == 'max_neighbor_cnt2_simple':
    assert(args.dc>0)
    t_outdir = maxneighborcnt_dir + '_perdist'
    create_dir(t_outdir)
    for filename in listdir(split_dir):
        cmd = ' '.join(['python max_neighbor_cnt2_simple.py',
            '-i', join(nb_dir, filename),
            '-r', args.seqfile,
            '-s', join(split_dir, filename),
            '-o', join(t_outdir, filename),
            '-dc', str(args.dc),
            '-j', str(args.njobs),
            ])
        print cmd
        system(cmd)
    system(' '.join(['touch {}'.format(t_outdir+'.done')]))


if args.order == 'nb_clust2':
    assert(args.dc>0)
    t_outdir = join(args.outdir, 'maxneighbor_clust_dc'+str(args.dc)+'_perdist2')
    create_dir(t_outdir)
    for filename in listdir(split_dir):
        print filename
        cmd = ' '.join(['python nb_clust2.py',
            '-f', join(maxneighborcnt_dir+'_perdist', filename),
            '-s', join(split_dir, filename),
            '-r', args.seqfile,
            '-o', join(t_outdir, filename),
            '-dc', str(args.dc),
            ])
        print cmd
        system(cmd)
    system(' '.join(['touch {}'.format(t_outdir+'.done')]))


if args.order == 'nb_clust2_w_rep':
    assert(args.dc>0)
    t_outdir = join(args.outdir, 'maxneighbor_clust_dc'+str(args.dc)+'_perdist2')
    create_dir(t_outdir)
    for filename in listdir(split_dir):
        print filename
        cmd = ' '.join(['python nb_clust2_w_rep.py',
            '-f', join(maxneighborcnt_dir+'_perdist', filename),
            '-s', join(split_dir, filename),
            '-r', args.seqfile,
            '-o', join(t_outdir, filename),
            '-dc', str(args.dc),
            ])
        print cmd
        system(cmd)
    system(' '.join(['touch {}'.format(t_outdir+'.done')]))


if args.order == 'combine_clust_w_rep':
    assert(args.dc>0)
    rep_pairs = []
    with open(args.replist) as f:
        for x in f:
            rep_pairs.append(x.split())

    for rep1, rep2, outfile in rep_pairs:
        if not exists(join(rep1, 'maxneighbor_clust_dc{}_perdist2'.format(args.dc))):
            raise Exception('not all pairs in {} and {} exists'.format(rep1, rep2))
        cmd = ' '.join(['python combine_clust_w_rep.py',
            '-rep1_dir', join(rep1, 'maxneighbor_clust_dc{}_perdist2'.format(args.dc)),
            '-rep2_dir', join(rep2, 'maxneighbor_clust_dc{}_perdist2'.format(args.dc)),
            '-dc', str(args.dc),
            '-o', outfile,
            ])
        print(cmd)
        system(cmd)

if args.order == 'clust':
    assert(exists(clust_cutoff_file))
    with open(clust_cutoff_file) as f:
        delta_cutoff = dict()
        for x in f:
            line = x.split()
            delta_cutoff[line[0]] = float(line[1])
    assert('others' in delta_cutoff)

    create_dir(clust_dir)
    for filename in listdir(split_dir):
        print filename
        t_cutoff = delta_cutoff[filename] if filename in delta_cutoff else delta_cutoff['others']
        cmd = ' '.join(['python clust_assign.py',
            '-f', join(feat_dir, filename),
            '-s', join(split_dir, filename),
            '-o', join(clust_dir, filename),
            '-rc', '0',
            '-dc', str(t_cutoff),
            '-j', str(args.njobs),
            ])
        print cmd
        system(cmd)
