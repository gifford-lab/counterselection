## Read parsing
Given a list of fastq read files, identify the CDR3 region using BLAST and translate to amino acid.

### Pipeline description
* First we run blastn-short to locate the most probable position of (1) header primer (head query) and (2) DY/DV + tail primer (tail query) in each read. Here we estimate the evalue cutoff needed to tolerant a given number of mismatch using simulation. And we use a word-size of `floor((len(query_seq)-1)/2)`, where `query_seq` is the one used in the search (header query or tail query). The optimal number of mismatch is picked by the dipping point on n_mismatch vs. n_wrong_len_seq plot (at this point most of the true CDR3, where there exist a low-noise query sequence,  have been recovered and the matches to false CDRs, where there are no real query sequences, are few). 

* Next, we convert the blast result into a python dictionary while only keeping the match with the lowest evalue for each read, and save it as a cPickle object.

* Next we split the read fasta file into small chunks. For each of the read chunk, we identify CDR by the following steps: 

	1.  Retrive the head query and tail query location in this read from the dictionary saved in cPickle.
	
	2.	Extract the sequence between the head query and the tail *primer* (so we keep the original DY/DV ending).
	
	3.  Check if the length is a non-zero multiple of three. 
	
### Usage
```
python main.py -i TOPDIR -o OUTDIR --headprimer HEAD --tailprimer TAIL --mismatch MISMATCH --command CMD \
	[--cdr3dir CDR3_DIR --logdir LOG_DIR --pept_outdir PEPT_DIR --sge_core SGE_CORE]
```

- `TOPDIR`: the folder that contains the read fastq file.
- `OUTDIR`: the output folder.
- `HEAD`: a FASTA file that contains the primer before the CDR.
- `TAIL`: a FASTA file that contains the primer after the CDR.
- `MISMATCH`: the max number of mismatch to allow in the BLAST search. The BLAST evalue cutoff for this mismatch will be estimated on the top 500 sequences.
- `CMD`: the order to carry out. Legal ones include:
	- 'fastq2fa': convert the read fastq file to fasta.
	- 'makedb': make a BLAST database for each fasta file using SGE.
	- 'blast': run BLAST using SGE. 
	- 'blast2dict': post-process the BLAST result and save as a dictionary per each experiment.
	- 'split': split the BLAST-ed result into chunks.
	- 'findCDR': segment the CDR for the sequences in each chunk using SGE. 
	- 'cat': concatenate the CDR result for all the chunks.
	- 'translate': translate the CDR into amino acids.
- `CDR3_DIR`: (Optional) the directory to save the CDR result. Default: $OUTDIR/$EXPT/cdr3.
- `LOG_DIR`: (Optional) the directory to save the logs during CDR segmentation. Default: $OUTDIR/$EXPT/log.
- `PEPT_DIR`: (Optional) the directory to save the translated peptide. Default: $OUTDIR/$EXPT/pept.
- `SGE_CORE`: (Optional) num of slots to occupy in SGE. Set it high to avoid crashing the memory of our nodes. Now only used in BLAST as it takes a lot of memory. Default: 2.

### Run on a toy dataset:
```
cd example
chmod +x download_toydata.sh
./download_toydata.sh

cd ..
python main.py -i example/test_input -o example/test_output --headprimer example/FW_head.fsa \
	--tailprimer example/FW_tail.fsa --mismatch 3 --command CMD
```

- `CMD`: see the "[Usage](#usage)" section.
