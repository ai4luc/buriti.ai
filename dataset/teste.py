import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

import scipy.io as sio
import os
import numpy as np
import torch
from torch.utils.data import Dataset
import random
import glob
import cv2
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, TensorDataset

device = torch.device("mps")

#image_path = "./histology/label/0TCGA-2Z-A9J9-01A-01-TS1.png"
image_path = './Potsdam/Potsdam_dataset/label/top_potsdam_2_10_label_noBoundary_0_0.tif'


class MyDataset(Dataset):
    '''
    dir_path: path to data, having two folders named data and label respectively
    '''

    def __init__(self, dir_path, transform=None, in_chan=3):
        self.dir_path = dir_path
        self.transform = transform
        self.data_path = os.path.join(dir_path, "data")
        self.data_lists = sorted(glob.glob(os.path.join(self.data_path, "*.tif")))
        self.label_path = os.path.join(dir_path, "label")
        self.label_lists = sorted(glob.glob(os.path.join(self.label_path, "*.tif")))

        self.in_chan = in_chan

    def __getitem__(self, index):
        img_path = self.data_lists[index]
        label_path = self.label_lists[index]
        if self.in_chan == 3:
            img = Image.open(img_path).convert("RGB")
        else:
            img = Image.open(img_path).convert("L")
        label = cv2.imread(label_path)
        label = cv2.cvtColor(label, cv2.COLOR_RGBA2GRAY)
        label_copy = label.copy()

        semantic_mask = label.copy()
        semantic_mask[semantic_mask == 0] = 0       # Edge
        semantic_mask[semantic_mask == 255] = 1     # Impervious surface
        semantic_mask[semantic_mask == 76] = 2      # Building
        semantic_mask[semantic_mask == 226] = 3     # Low vegetation
        semantic_mask[semantic_mask == 150] = 4     # Tree
        semantic_mask[semantic_mask == 179] = 5     # Car
        semantic_mask[semantic_mask == 29] = 6      # Background

        label_copy[label_copy == 0] = 0     # Edge
        label_copy[label_copy == 255] = 1   # Impervious surface
        label_copy[label_copy == 76] = 2    # Building
        label_copy[label_copy == 226] = 3   # Low vegetation
        label_copy[label_copy == 150] = 4   # Tree
        label_copy[label_copy == 179] = 5   # Car
        label_copy[label_copy == 29] = 6    # Background

        instance_mask = self.sem2ins(label_copy)
        normal_edge_mask = self.generate_normal_edge_mask(label)
        cluster_edge_mask = self.generate_cluster_edge_mask(label)

        if self.transform is not None:
            seed = 666
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            #torch.cuda.manual_seed(seed)
            torch.mps.manual_seed(seed)
            img = self.transform(img)
            label = self.transform(label)
        else:
            T = transforms.Compose([
                transforms.ToTensor()
            ])
            img = T(img)
            img = img
            semantic_mask = torch.tensor(semantic_mask)
        img = img.to(device)
        semantic_mask = semantic_mask.to(device)
        instance_mask = torch.tensor(instance_mask).to(device)
        normal_edge_mask = torch.tensor(normal_edge_mask).to(device)
        cluster_edge_mask = torch.tensor(cluster_edge_mask).to(device)
        return img, instance_mask, semantic_mask, normal_edge_mask, cluster_edge_mask

    def __len__(self):
        return len(self.data_lists)

    def sem2ins(self, label):
        seg_mask_g = label.copy()

        # seg_mask_g[seg_mask_g != 255] = 0
        # seg_mask_g[seg_mask_g == 255] = 1

        contours, hierarchy = cv2.findContours(seg_mask_g, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for i in range(len(contours)):
            cnt = contours[i]
            seg_mask_g = cv2.drawContours(seg_mask_g, [cnt], 0, i + 1, -1)
        return seg_mask_g

    def generate_normal_edge_mask(self, label):

        normal_edge_mask = label.copy()

        normal_edge_mask[normal_edge_mask == 0] = 1
        normal_edge_mask[normal_edge_mask == 255] = 0
        normal_edge_mask[normal_edge_mask == 76] = 0
        normal_edge_mask[normal_edge_mask == 226] = 0
        normal_edge_mask[normal_edge_mask == 150] = 0
        normal_edge_mask[normal_edge_mask == 179] = 0
        normal_edge_mask[normal_edge_mask == 29] = 0

        return normal_edge_mask

    # It will do same previous task, i.e., edge detection
    def generate_cluster_edge_mask(self, label):

        cluster_edge_mask = label.copy()

        cluster_edge_mask[cluster_edge_mask == 0] = 1
        cluster_edge_mask[cluster_edge_mask == 255] = 0
        cluster_edge_mask[cluster_edge_mask == 76] = 0
        cluster_edge_mask[cluster_edge_mask == 226] = 0
        cluster_edge_mask[cluster_edge_mask == 150] = 0
        cluster_edge_mask[cluster_edge_mask == 179] = 0
        cluster_edge_mask[cluster_edge_mask == 29] = 0

        return cluster_edge_mask


data_path = image_path
total_data = MyDataset(dir_path=data_path)
train_set_size = int(len(total_data) * 0.8)
test_set_size = len(total_data) - train_set_size
train_set, test_set = data.random_split(total_data, [train_set_size, test_set_size],
                                                generator=torch.Generator().manual_seed(random_seed))

trainloader = torch.utils.data.DataLoader(train_set, batch_size=2, shuffle=True)
testloader = torch.utils.data.DataLoader(test_set, batch_size=2, shuffle=False)
