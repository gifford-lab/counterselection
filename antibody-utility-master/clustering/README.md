## Clustering
Given a distance cutoff, cluster the sequences by finding all the connected components in a graph where each node is a sequence and any two nodes between which the Levenstein distance is less than the cutoff is connected by an edge.

This algorithm has a complexity of O(N^2). Thus we only do this on a subset of sequences (seed sequences) that have high read counts, and determine the cluster of the rest sequences by matching with the seeds. When a nonseed is close to multiple seed sequences, the most common seed cluster is used. The complexity of the algorithm is O(L^2) + O(NxL) where L is the number of seeds and N is the total number of sequences. 

### Usage

```
python cluster.py -i INPUT_TSV -o OUT_DIR --ns N_SEED -c CUTOFF -j N_JOBS -b BATCH_SIZE --command COMMAND
```

- `INPUT_TSV`: the path to a TSV file where the first column is sequence and the second column is the corresponding counts.
- `OUT_DIR`: the output directory
- `N_SEED`: the number of seeds. (default: 10^5)
- `CUTOFF`: the distance cutoff. (default: 2)
- `N_JOBS`: the number of process to run in parallel. (default: 16)
- `BASTCH_SIZE`: the number of rows of the distance matrix assigned to each process. (default: 1000)
- `COMMAND`: a comma-delimited string that concatenates any combinations of the following commands. Regardless of their order in `COMMAND`, all the commands will be parsed and executed in the following order:
	- 'preprocess': preprocessing
	- 'dist_seed': calculate the distance matrix of the seeds.
	- 'dist_nonseed': calcualte the distance from each nonseed sequence to the seeds.
	- 'find_nb_seed': identify the neighbors of each seed given a cutoff
	- 'clust_seed': perfectly cluster the seeds.
	- 'find_nb_nonseed': identify the seed neighbors of each nonseed given a cutoff
	- 'clust_nonseed': project the nonseeds to the seeds to identify their cluster assignment. (**This step is required even there is no nonseed sequences**)
	- 'output': output the clustering result to file ("$OUT_DIR/clusters")

We can also calculate the distance from all the sequences to a target sequence. To do this, we need to complete 'preprocess' step above first and do the following:

```
python cluster.py -i INPUT_TSV -o OUT_DIR -j N_JOBS -b BATCH_SIZE \
	--command single_seq_dist --target_seq SEQ --target_outfile OUTFILE
```

- `INPUT_TSV`, `OUT_DIR`, `N_JOBS`, `BATCH_SIZE`: same as above.
- `SEQ`: the sequence to calculate distance to.
- `OUTFILE`: the file to save the distances from all the sequences in `INPUT_TSV` to the target sequence, one distance per line.
