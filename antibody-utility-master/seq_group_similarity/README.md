## Match two groups of sequences
For each sequence in one group, calculate the minimal edit distance of it to another group of sequence.

### Usage
```
python seq_match.py --tsv1 TSV1 --tsv2 TSV2 --mode MODE --outputfile OUTPUT_FILE --jobs JOBS --strip PADDING
```

- `TSV1`: a TSV file of a group of sequences. For each of sequences, the min distance to the sequences in `TSV2` will be calculated.
- `TSV2`: a TSV file of the group of sequences to compare against.
- `MODE`: 'exact' or 'shift' for exact matching or shift matching.
- `OUTPUT_FILE`: the file to save the matching result.
- `JOBS`: (optional) the number of processes to run in parallel (default: 16)
- `PADDING`: (optional) the padding sequence to get rid of (default: '')
