import argparse, sys, numpy as np, cPickle, multiprocessing as mp
from os.path import dirname, basename, join, exists, abspath
from os import system, makedirs, listdir, walk
from tempfile import NamedTemporaryFile

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='inputdir', type=str, help='top directory of the folder that contains the fastq file')
    parser.add_argument('-o', dest='outdir', type=str, help='the output directory')
    parser.add_argument('--headprimer', type=str, help='a file that contains the head primer sequence')
    parser.add_argument('--tailprimer', type=str, help='a file that contains the tail primer sequence')
    parser.add_argument('--mismatch', type=int, help='the max number of mismatch to allow in the BLAST search')
    parser.add_argument('--batchsize',default='800000',type=str,help='size of small batches when splitting the FASTA file for fast segmentation,DEFAULT=800000')
    parser.add_argument('--cdr3dir', default='', help='the directory to save the cdr result')
    parser.add_argument('--logdir', default='', help='the directory to save the logs in CDR segmentation')
    parser.add_argument('--pept_outdir', default='', help='the directory to save the translated amino acid fasta files')
    parser.add_argument('--command', type=str, help='the order to carry out')
    parser.add_argument('--sge_core', type=int, default=2)
    return parser.parse_args()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
        return i + 1

def create_dir(mydir):
    if not exists(mydir):
        makedirs(mydir)

def findFA(mydir):
    for x in listdir(mydir):
        if x[-3:] == '.fa':
            yield x

def findCutoff(primer, fafile):
    with open(primer) as f:
        f.readline()
        t_primer = f.readline().strip()
    myfa = NamedTemporaryFile().name
    myalign = myfa + '.algn'
    with open(fafile) as f, open(myfa, 'w') as fout:
        d = [x for x in f]
        d[-1] = t_primer[:(len(t_primer)-args.mismatch)] + ''.join(['N']*args.mismatch) + d[-1][len(t_primer):]
        for x in d:
            fout.write(x)

    system(' '.join(['/cluster/geliu/software/blast2.6/bin/makeblastdb -dbtype nucl -in', myfa, '-out', myfa, '-logfile', myfa+'.log']))
    system(' '.join(['/cluster/geliu/software/blast2.6/bin/blastn -task blastn-short -query', primer, '-out', myalign,
                     '-outfmt 6 -max_target_seqs 500000 -word_size', str((len(t_primer)-1)/2), '-evalue 500000', '-strand plus -db', myfa]))
    with open(myalign) as f:
        for x in f:
            line = x.split()
            if line[3] == str(len(t_primer)-args.mismatch):
                return float(line[-2])
        raise ValueError('Can\'t find the target number of mismatch. Something went wrong')

def primerLen(primer_file):
    with open(primer_file) as f:
        f.readline()
        return len(f.readline().strip())

def findFASTQ(directory):
    for dirpath, _, files in walk(directory):
        for file in files:
            if file.endswith('.fastq.gz'):
                yield join(dirpath, file)

args = parse_args()

pwd = abspath(dirname(__file__))
topdir = abspath(args.inputdir)
outdir = abspath(args.outdir)
cdr3_outdir = args.cdr3dir or join(outdir, 'cdr3')
logdir = args.logdir or join(outdir, 'log')
pept_outdir = args.pept_outdir or join(outdir, 'pept')
seqtk = '/afs/csail.mit.edu/group/cgs/software/seqtk/seqtk seq -A'
transeq = '/cluster/geliu/software/EMBOSS-6.6.0/emboss/transeq'

if args.command not in ['fastq2fa', 'makedb', 'blast', 'split', 'findCDR', 'cat', 'translate', 'findcutoff', 'blast2dict']:
    raise ValueError('Unrecognized order {}'.format(args.command))
create_dir(outdir)

if args.command == 'fastq2fa':
    for x in findFASTQ(topdir):
        system(' '.join([seqtk, x, '| tr \"#\" \"_\" | tr \":\" \"_\" >', join(outdir, basename(x).split('_')[0]+'.fa') ]))

if args.command == 'makedb':
    create_dir(logdir)
    template = 'echo  \"/cluster/geliu/software/blast2.6/bin/makeblastdb -dbtype nucl -in {} -out {}\"| /usr/bin/qsub -e {} -o {} -N {} -wd `pwd`'
    for x in findFA(outdir):
        prefix = x.split('.fa')[0]
        if not exists(prefix + '.nsq'):
            system(template.format(join(outdir, x), join(outdir, prefix), logdir, logdir, 'makedb_'+prefix))

if args.command == 'blast':
    create_dir(logdir)
    headprimer_len, tailprimer_len = primerLen(args.headprimer), primerLen(args.tailprimer)
    for x in findFA(outdir):
        fileprefix = x.split('.fa')[0]
        full_prefix = join(outdir, fileprefix)
        tmpfile = NamedTemporaryFile().name
        system(' '.join(['head -n 1000', join(outdir, x), '>', tmpfile]))
        template = 'echo  \"/cluster/geliu/software/blast2.6/bin/blastn -task blastn-short -query {} -out  {}_{}.algn -outfmt 6 -max_target_seqs 1000000000 -word_size {}  -evalue {} -strand plus -db {}\"| /usr/bin/qsub -e {} -o {} -N {} -wd `pwd` -pe test {}'
        system(template.format(args.headprimer, full_prefix, 'head', (headprimer_len-1)/2, findCutoff(args.headprimer, tmpfile)*file_len(join(outdir, x))/1000.0,
            full_prefix, logdir, logdir, fileprefix+'_head', args.sge_core))
        system(template.format(args.tailprimer, full_prefix, 'tail', (tailprimer_len-1)/2, findCutoff(args.tailprimer, tmpfile)*file_len(join(outdir, x))/1000.0,
            full_prefix, logdir, logdir, fileprefix+'_tail', args.sge_core))

if args.command == 'blast2dict':
    def read_blast(filename, id_col, data_cols, eval_col, delimiter='\t'):
        d = dict()
        with open(filename) as f:
            for x in f:
                line = np.asarray(x.split(delimiter))
                t_id = line[id_col]
                if t_id not in d or float(line[eval_col]) < d[t_id][-1]:
                    d[t_id]= map(float, line[data_cols + [eval_col]])
        return d

    def blast2dict(args):
        outdir, x = args[:]
        prefix = x.split('.fa')[0]
        hits_head = read_blast(join(outdir, prefix+'_head.algn'), id_col=1, data_cols=[7,9], eval_col=10)
        hits_tail = read_blast(join(outdir, prefix+'_tail.algn'), id_col=1, data_cols=[6,8], eval_col=10)
        with open(join(outdir, prefix+'_algn_dict.pkl'), 'wb') as f:
            cPickle.dump([hits_head, hits_tail], f, protocol=cPickle.HIGHEST_PROTOCOL)

    mp_args = [[outdir, x] for x in findFA(outdir)]
    pool = mp.Pool(processes=8)
    pool.map(blast2dict, mp_args)
    pool.close()
    pool.join()

if args.command == 'split':
    for x in findFA(outdir):
        system(' '.join(['split -d -l '+ args.batchsize, join(outdir, x), join(outdir, x.split('.fa')[0]+'_small')]))

if args.command == 'findCDR':
    create_dir(cdr3_outdir)
    create_dir(logdir)

    template = 'echo  \"python ' + join(pwd, 'find_CDR_seqs.py') + ' --blastdict {} --fasta {} --header_len {} 2>{} 1>{} \"| /usr/bin/qsub -e SGElog -o SGElog -N {} -wd `pwd`'
    headprimer_len = primerLen(args.headprimer)

    for x in findFA(outdir):
        prefix = x.split('.fa')[0]
        for smallfile in listdir(outdir):
            if smallfile.split('_small')[0] == prefix:
                system(template.format(join(outdir, prefix+'_algn_dict.pkl'), join(outdir, smallfile), headprimer_len, join(logdir, smallfile), join(cdr3_outdir, smallfile+'_cdr3.fa'), smallfile))

if args.command == 'cat':
    for x in findFA(join(outdir)):
        prefix = x.split('.fa')[0]
        smallfiles = np.sort([smallfile for smallfile in listdir(outdir) if smallfile.split('_small')[0] == prefix])
        system(' '.join(['cat'] + [join(cdr3_outdir, small+'_cdr3.fa') for small in smallfiles] + ['>', join(cdr3_outdir, prefix+'_cdr3.fa')]))

if args.command == 'translate':
    create_dir(pept_outdir)
    for x in listdir(cdr3_outdir):
        if 'small' not in x:
            system(' '.join([transeq, join(cdr3_outdir, x), join(pept_outdir, x.split('_cdr3')[0]+'_pept.fa')]))
