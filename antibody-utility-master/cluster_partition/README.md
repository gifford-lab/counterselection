## Cluster partition
Given the output from clustering utility, which is a tsv of sequence, its counts, its cluster and the size of its cluster, we partition the clusters into groups with desired sizes (for instance train/valid/test set). We use recursion (implemented by stacks) to identify the allocation the size of which match the requirement up to certain tolerance level.

The lowest tolerance level will be tried with first. We permute the groups before the matching and when the tolerance level is nonzero, every run can return a different allocation even when the perfect allocation is unique. Run on the toy dataset (see below) several times as an example.  

### Usage

```
python main.py -i INPUTFILE --outdir OUTDIR --outfiles OUTFILES --ratios RATIOS --tolratio TOL
```

- `INPUTFILE`: the output from the clustering utility, i.e. a tsv file of four columns: a sequence, its read count / enrichment, its cluster, the size of its cluster. The first row is a header.
- `OUTDIR`: the directory under which to save the output.
- `OUTFILES`: a underscore-delimited string that denotes the name of the outputfiles for each group (for instance "train_valid_test" for three files $OUTDIR/train, $OUTDIR/valid and $OUTDIR/test.
- `RATIOS`: a underscore-delimited string that denotes the ratio of the size of each group to the total number of sequences.
- `TOL`: the ratio of the tolerance level to the total number of sequences.

### Run on toy dataset:
The following command takes the file at "example/input" and generates three files "1", "2" and "3" under the current directory, which corresponds to three groups of size of 0.8, 0.1 and 0.1 of the total number of the sequences. And the matching tolerance is 0.02 of the total number of sequences.

```
python main.py -i example/input --outdir . --outfiles 1_2_3 --ratios 0.8_0.1_0.1 --tolratio 0.02
```

