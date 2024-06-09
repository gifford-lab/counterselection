## parametric-tSNE


### Usage
Given a list of sequences, split them into chunks of `BATCHSIZE` samples and calculate the similarity matrix `P` used in tSNE for sequences in the same chunk. The output is a (BATCHSIZE*num_batch) x BATCHSIZE matrix that is saved in hdf5 format and ready to be trained on using a NN, where `num_batch` = sample_len // BATCHSIZE.

```
python cal_p.py TSV_FILE OUTFILE MODE OUTLEN BATCHSIZE
```

- `TSV_FILE`: a file of sequences (one column)
- `OUT_FILE`: the output file prefix. Every 10 batch will be saved to ${OUT_FILE}.h5.batchX where X is the file index.
- `MODE`: 'aa' or 'dna' for amino acid or DNA sequences
- `OUTLEN`: every sequence will be padded to this length using 'N' (mode='dna') or 'J' (mode='aa')
- `BATCHSIZE`: batchsize of the neural network. We will split the data into chunks of this size and calculate the pair-wise distance of samples in the same batch.

Next, train a NN with `tsne` loss as defined in 'models/64_3c_3s_32f_nopool_bs5000.py'.

**Important things to note:**

- make sure no shuffling is used during training (Keras for instance will shuffle the samples by default in `model.fit`).
- make sure to use the same batch size used when calculating the similarity matrix.

### Example on toy data
Calculate similarity matrix:

```
cd toydata
mkdir output
python ../cal_p.py train.seq output/train aa 8 5000
python ../cal_p.py valid.seq output/valid aa 8 5000
```

Train a parametric-tSNE and predict on the training set:

```
cd toydata
python $KERAS_GENOMICS_DIR/main.py -d output -m ../models/64_3c_3s_32f_nopool_bs5000.py  -shuf 0 --patience 300 -bs 5000 -y -t -te 100 -p output/train.h5.batch
```

where `KERAS_GENOMICS_DIR` is the path to [Keras-genomics](https://github.com/gifford-lab/keras-genomics) repository.

