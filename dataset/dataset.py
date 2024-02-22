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

# On NVIDIA architecture
#device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# On Apple M chip architecture
# device = torch.device("mps")
#print('Using ' + str(device) + ' GPU')


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
        label_name = os.path.basename(label_path)
        label = cv2.cvtColor(label, cv2.COLOR_RGBA2GRAY)
        label_copy = label.copy()

        print(label_name)

        semantic_mask = label.copy()
        semantic_mask[semantic_mask == 0] = 0  # Edge
        semantic_mask[semantic_mask == 255] = 0  # Impervious surface
        semantic_mask[semantic_mask == 76] = 1  # Building
        semantic_mask[semantic_mask == 226] = 2  # Low vegetation
        semantic_mask[semantic_mask == 150] = 3  # Tree
        semantic_mask[semantic_mask == 179] = 4  # Car
        semantic_mask[semantic_mask == 29] = 5  # Background

        label_copy[label_copy == 0] = 0  # Edge
        label_copy[label_copy == 255] = 0  # Impervious surface
        label_copy[label_copy == 76] = 1  # Building
        label_copy[label_copy == 226] = 2  # Low vegetation
        label_copy[label_copy == 150] = 3  # Tree
        label_copy[label_copy == 179] = 4  # Car
        label_copy[label_copy == 29] = 5  # Background

        if self.transform is not None:
            seed = 666
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed(seed)
            # torch.mps.manual_seed(seed)
            img = self.transform(img)
            label = self.transform(label)
        else:
            T = transforms.Compose([
                transforms.ToTensor()
            ])
            img = T(img)
            img = img
            semantic_mask = torch.tensor(semantic_mask, dtype=torch.int32)
        #img = img.to(device)
        #semantic_mask = semantic_mask.to(device)
        return semantic_mask

    def __len__(self):
        return len(self.data_lists)
