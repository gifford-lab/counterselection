import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from sklearn import metrics
import math

import torch
import torch.nn as nn
from torch.nn import functional as F
import torch.utils.data

from torch.nn.parameter import Parameter
from torch.nn import init

from tqdm import tqdm
from model import *

def compute_pred_labels(ensemble_path, seqs):
    models = [Seq_32_32(), Seq32x1_16(), Seq32x2_16(), Seq64x1_16(), Seq_emb_32x1_16(),  Seq32x1_16_filt3()]
    with torch.no_grad():
        overall_preds=[]
        #pbar = loader
        for model in models:
            preds=[]
            truths=[]
            net = model
            net.load_state_dict(torch.load(ensemble_path+str(model).split("(")[0]+"/best.pt", map_location="cpu"))
            net = net.cpu()
            net = net.eval()
            data = seqs.cpu()
            pred = 1-np.array(list(map(np.argmax,net(data).cpu().numpy())))
            overall_preds.append(pred)
        ensemble_preds = stats.mode(np.array(overall_preds), axis=0)[0]
    return ensemble_preds

# def compute_pred_labels(ensemble_path, loader, device):
#     models = [Seq_32_32(), Seq32x1_16(), Seq32x2_16(), Seq64x1_16(), Seq_emb_32x1_16(), Seq32x1_16_filt3()]
#     with torch.no_grad():
#         overall_preds=[]
#         pbar = tqdm(loader, position=0, leave=True)
#         #pbar = loader
#         for model in models:
#             preds=[]
#             truths=[]
#             for (data, target, bounds) in pbar:
#                 #data = truncate(data, bounds).cuda()
#                 net = model
#                 net.load_state_dict(torch.load(ensemble_path+str(model).split("(")[0]+"/best.pt"))
#                 net = net.to(device)
#                 net = net.eval()
#                 data = data.to(device)
#                 pred = 1-np.array(list(map(np.argmax,net(data).cpu().numpy())))
#                 #preds.append( net(data).cpu().numpy() )
#                 preds.append(pred)
#                 truth=1-np.array(list(map(np.argmax, target.numpy())))
#                 truths.append(truth)
#             preds = np.concatenate(preds)
#             truths = np.concatenate(truths)
#             overall_preds.append(preds)
#         ensemble_preds = stats.mode(np.array(overall_preds), axis=0)[0]
#     return ensemble_preds.reshape(-1), truths

# def compute_pred_logits(ensemble_path, loader):
#     models = [Seq_32_32(), Seq32x1_16(), Seq32x2_16(), Seq64x1_16(), Seq_emb_32x1_16(), Seq32x1_16_filt3()]
#     with torch.no_grad():
#         overall_preds=[]
#         pbar = tqdm(loader, position=0, leave=True)
#         #pbar = loader
#         for model in models:
#             preds=[]
#             truths=[]
#             for (data, target, bounds) in pbar:
#                 #data = truncate(data, bounds).cuda()
#                 net = model
#                 net.load_state_dict(torch.load(ensemble_path+str(model).split("(")[0]+"/best.pt"))
#                 net = net.to(device)
#                 net = net.eval()
#                 data = data.to(device)
#                 pred = net(data).cpu().tolist()
#                 pred = [elt[0] for elt in pred]
#                 preds.append(pred)
#                 target = [elt[0] for elt in target]
#                 truths.append(target)
#             preds = np.concatenate(preds)
#             truths = np.concatenate(truths)
#             overall_preds.append(preds)
#         ensemble_preds = np.average(np.array(overall_preds), axis=0)
#     return ensemble_preds, truths