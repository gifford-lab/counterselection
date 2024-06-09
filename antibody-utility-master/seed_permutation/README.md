## Sequence permutation
Give a list of seed sequences and a list of new sequences optimized from each of the seed by some method, perform random permutation to each of the seed with the distribution of the number of changes for each seed length matched to the optimization method. 

### Usage

```
python permute.py SEED PROPOSED N_TRIAL OUT_DIR
```

- `SEED`: a TSV file of the seed sequences. The first column is ID and the second column is the sequence. Same format apply to any other TSV input for this repository. 
- `PROPOSED`: a TSV file of sequences optimized from each of the seed sequences by some other method. We will match the distribution of number of bases changed to this method when doing permutation.
- `N_TRIAL`: the number of permutations we will perform.
- `OUT_DIR`: the directory to save the result (one file for each permutation). Additionally, a file named "distance_summary" that records the number of changes between each seed and the corresponding optimized sequence will be saved.
