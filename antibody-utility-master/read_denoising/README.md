## Read denoising
Fit a Poisson-mixture model to denoise the read counts.

### Perform model selection to select the number of mixtures
Pick a reasonable number of mixtures by finding the elbow point in the num of mixture vs. likelihood plot generated.

```
python main.py -i CSV_FILE -o OUT_DIR --mc MAX_CLUST -p PARAM_FILE --command model_select [-t N_TRIAL]
```

- `CSV_FILE`: a csv file of sequences and counts
- `OUT_DIR`: the output directory. The result will be saved under $OUT_DIR/model_select, including plots of num of mixture vs. likelihood and a Pickle file of the intermediate data.
- `MAX_CLUST`: the max number of clusters to try in model selection
- `PARAM_FILE`: a tab-delimited file with two columns ([example](https://github.com/gifford-lab/antibody-utility/blob/master/read_denoising/example/paramfile)). The first column specifies the name of the rounds to denoise, and the second column specifies the name of the corresponding previous round (to get the sequences with zero counts in the current round). **Thus this procedure can't be used to denoise the read counts in round zero**.
- `N_TRIAL`: (Optional) num of trials when performing model selection (default: 10).



### Denoise the counts with a mixture model trained with a given number of mixtures
The mixture with the lowest Poisson parameter will be removed. All the other counts will be deducted by this parameter.

```
python main.py -i CSV_FILE -o OUT_DIR --clust_n_file  CLUST_N_FILE  --command denoise
```

- `CSV_FILE`: a csv file of sequences and the corresponding counts
- `OUT_DIR`: the output directory. The denoise results will be saved under $OUT_DIR/denoise, including a CSV file of the denoise read counts, a CSV file of the intermediate stats, and histograms of the reads to remove (in red) and the reads to keep (green) for each round.
- `CLUST_N_FILE`: a tab-delimited file of two columns, round name and the number of mixtures ([example](https://github.com/gifford-lab/antibody-utility/blob/master/read_denoising/example/clust_n_file)).


### Run on toy data:
```
python main.py -i example/example.csv -o example/output --mc 6 -p example/paramfile --command model_select
python main.py -i example/example.csv -o example/output --clust_n_file example/clust_n_file --command denoise
```
