import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import random
import pickle

def generate_round_df(raw_path):
    """
    Function to compute round-by-round enrichment and store as a pd.DataFrame. 
    
    Inputs:
    -------
    raw_path: Path to folder containing CDR peptide read files (usually aa/ folder in analysis folder).
    """
    pass

def make_read_txt(path):
    total_reads=0       
    counts_dict={}
    for dataset in os.listdir(path+"aa/"):
        with open(path+"aa/"+dataset, "r") as f:
            outfile = open(path+"reads/"+dataset+".txt", "w")
            counter=1
            for line in f:
                if counter % 2==0:
                    outfile.write(line)
                    counter+=1
                else:
                    pass
                    counter+=1
                    
def create_count_dict(path):
    """
    Function to generate count dictionaries. 
    """
    
    # pass path to read txt file and output dictionary of unique counts and pickle it
    for dataset in os.listdir(path+"reads/"):
        with open(path+"reads/"+dataset, "r") as f:
            count_dict={}
            for line in f:
                line=line.strip()
                if line in count_dict:
                    count_dict[line]+=1
                else:
                    count_dict[line]=1
            pickle.dump(count_dict, open("{}/count_dicts/{}_count_dict.pkl".format(path,dataset.split("_")[0]), "wb"))
            
            
def make_enrichment_df(r1_count_dict_path, r2_count_dict_path, r3_count_dict_path):
    """
    Function for making pandas DataFrame with reads per round stored. 
    """
    # Read in Round 1
    with open(r1_count_dict_path, 'rb') as f:
        count_dict = pickle.load(f)
        f.close()
    r1 = pd.DataFrame(count_dict.values(), index=count_dict.keys(), columns=['R1'])
    
    # Read in Round 2
    with open(r2_count_dict_path, 'rb') as f:
        count_dict = pickle.load(f)
        f.close()
    r2 = pd.DataFrame(count_dict.values(), index=count_dict.keys(), columns=['R2'])

    # Read in Round 3
    with open(r3_count_dict_path, 'rb') as f:
        count_dict = pickle.load(f)
        f.close()
    r3 = pd.DataFrame(count_dict.values(), index=count_dict.keys(), columns=['R3'])
    
    # Return DataFrame´
    return r1.merge(r2, right_index=True, left_index=True, how='outer').merge(r3, right_index=True, left_index=True, how='outer')
            

def make_class_set(enrichment_df):
    """
    Function to generate a classification dataset. 
    
    Inputs:
    -------
    enrichment_df: pd.DataFrame()
        Output of make_enrichment_df() with round 3 and round 2 counts.
    """
    full = enrichment_df
    
    # drop sequences with * terminal AA
    to_drop_full = []
    to_drop_test = []
    for seq in full.index:
        if "*" in seq or len(seq)>20:
            to_drop_full.append(seq)
    full = full.drop(labels=to_drop_full)
    full["R3"].fillna(0.0, inplace=True)
    full["R2"].fillna(0.0, inplace=True)
    full["R1"].fillna(0.0, inplace=True)
    
    # Filtering Criteria
    full=full[((full["R3"]>=3.0) | (full["R2"]>=3.0) | (full["R1"]>=3.0)) | 
      ((full["R3"]>=1.0) & (full["R2"]>=1.0) & (full["R1"]>=1.0))]
    enrichment = np.log10(np.array(full.iloc[:,-1]+1)/np.array(full.iloc[:,-2]+1))
    
    # Label data with tolerance
    labels = []
    labels2 = []
    for idx in range(len(full)):
        if full.iloc[idx,-1]-full.iloc[idx,-2]>1e-6:
            labels.append(1)
            labels2.append(0)
        elif full.iloc[idx, -1]<5e-5 or full.iloc[idx,-1]-full.iloc[idx,-2]<1e-6:
            labels.append(0)
            labels2.append(1)
    return pd.DataFrame({"l": labels, "l2": labels2}, index=full.index)    