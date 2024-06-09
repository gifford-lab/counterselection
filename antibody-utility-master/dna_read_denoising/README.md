# DNA read denoising
Here we provide two methods to denoise the DNA reads.

## Preprocessing
For all the methods to work, we need to preprocess the reads first (a FASTA file). The following commands identify the uniq sequences, split them by length, and further divide each into batches.

```
python main.py -s SEQFILE -o OUTDIR -c uniq
python main.py -s SEQFILE -o OUTDIR -c split
python main.py -s SEQFILE -o OUTDIR -c prep_dist
```

- `SEQFILE`: the read FASTA file. **Same below**.
- `OUTDIR`: the output directory. **Same below**.

## Method 1: clustering by fast search and find of density peaks
Described in Rodriguez et al (Science 2014).

#### Calculate distance matrix

```
python main.py -s SEQFILE -o OUTDIR  -c dist
```

#### Calculate rho and delta

```
python main.py -s SEQFILE -o OUTDIR -dc DC -c feat
```

- `DC`: the distance cutoff (strictly less than) as defined in the paper to define neighbors and calculate rho. 2 was used in the previous analysis (i.e. considering 1bp neighbors).


#### Cluster the sequences
Under `OUTDIR`, create a tab-delimited file named `delta_cutoff` with two columns to map from a length to a delta cutoff. The first column should be `lenX` where X is a number denoting the length. The second column should be float numbers that correspond to the delta cutoff to be used for sequences with that length.

```
python main.py -s SEQFILE -o OUTDIR -c clust
```

## Method 2: a probablistic model based on distance and read count
As described in Liu et al.

#### Identify the most aboundant neighboring sequence in various distance ranges
We look at neighbors <=3bp.

##### (Implementation 1)Use a distance matrix

```
python main.py -s SEQFILE -o OUTDIR  -c dist
python main.py -s SEQFILE -o OUTDIR -dc 4 -c max_neighbor_cnt2
python main.py -s SEQFILE -o OUTDIR -dc 4 -c nb_clust2
```

##### (Implementation 2)Not using a distance matrix
This is faster than implementation 1 because it doesn't generate a distance matrix but only records the neighbor of each sequence within a fixed radius. As a consequence, if you want to try a few different neighborhood radiuses, you will spend more time.

```
python main.py -s SEQFILE -o OUTDIR -c find_nb
```

Alternatively, you can also use `-c find_nb_single` to spawn threads on the same computational node (suitable for EC2).

After all the jobs are finished:

```
python main.py -s SEQFILE -o OUTDIR -dc 4 -c max_neighbor_cnt2_simple
python main.py -s SEQFILE -o OUTDIR -dc 4 -c nb_clust2
```

## Method 3: method 2 but also consider the replicates

Instead of calculating p_NMLk, we evaluate q_NMLk for the two replicates of the same experiment and calculate their product. Essentially we remove a sequence when it is considered as noise (including not showing up) in both replicates. Refer to Liu et al. for the definition of p_NMLk and q_NMLk.

First run method 2 except replacing the "nb_clust2" argument in the last step with "nb_clust2_w_dup".

Then create a tab-delimited file of three columns to specify the "OUTDIR" of each pair of replicates (column 1 and 2) and the path of a file to save the denoising results for this pair (column 3). Run the following command with `DUP_FILE` being the path to this file:

```
python main.py -s haha -o haha -dc 4 -c combine_clust_w_dup -duplist DUP_FILE
```

- `haha`: here "-s" and "-o" are not used so you can use any place-holder but these arguments are required (to fix in the future).
