# Steps for processing raw data
The below is an example of processing raw data from sequencing of affinity selection experiments collected on an Illumina HiSeq/MiSeq machine of CDR3 diversified libraries. These processing steps should be followed for any new data wit

## Unzip antibody-utility (shared by request) in a Python 2 environment (recommend conda)
```
unzip antibody-utility-master.zip
mv antibody-utility-master antibody-utility
```

## `/processing_example` directory
The provided directory in this repo contains the folders needed to run the data preprocessing steps below. An example set of files is provided in `processing_example/raw`. For custom analysis on new targets, generate a similar folder with raw reads stored in the `*/raw` folder. 
```
mkdir processing_example/
mkdir processing_example/raw
mkdir processing_example/aa  
mkdir processing_example/cdr  
mkdir processing_example/fas
mkdir processing_example/reads
mkdir processing_example/split
mkdir processing_example/count_dicts
```

## Unzip antibody-utility (shared by request) in a Python 2 environment (recommend conda)
```
unzip antibody-utility-master.zip
```

## Define the created directory as TOPDIR
```
TOPDIR="./processing_example/"
```

## Convert .fastq files to .fa format
```
python ./antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'fastq2fa'
```

## Create a BLAST database
```
python ./proj/antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'makedb'
```

## Run BLAST
```
python ./proj/antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'blast' --sge_core 5
```

## Run BLAST2dict
```
python ./proj/antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'blast2dict' --sge_core 3
```

## Split files
```
python ./proj/antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'split' --sge_core 3
```

## Find CDR seqeunce using head and tail pattern
```
python ./antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'findCDR' --sge_core 3 --cdr3dir $TOPDIR/cdr/ --logdir $TOPDIR/cdr/log
```

## Final processing 
```
python ./antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa \
--tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'cat' --sge_core 3 --cdr3dir $TOPDIR/cdr/
```

```
python ./antibody-utility/read_parsing/main.py -i $TOPDIR/raw/ -o $TOPDIR/fas/ --headprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_head.fsa -\
-tailprimer /data/gl/g2/sachit/proj/antibody-utility/read_parsing/example/FW_tail.fsa --mismatch 3 --command 'translate' --sge_core 3 --cdr3dir $TOPDIR/cdr/ --pept_outdir $TOPDIR/aa/

```

## The directory is now prepared for `counterselection/notebooks/Preprocessing-demo.ipynb`