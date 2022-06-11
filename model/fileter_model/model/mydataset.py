#coding:utf8

import os
import cv2
import numpy as np
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, dirname):
        super(MyDataset, self).__init__()
        self.images = []
        self.labels = []
        postive_paths = os.listdir(os.path.join(dirname, '1'))
        negtive_paths = os.listdir(os.path.join(dirname, '0'))
        for p in postive_paths:
            self.labels.append(1)
            self.images.append(os.path.join(dirname, '1', p))
        for p in negtive_paths:
            self.labels.append(0)
            self.images.append(os.path.join(dirname, '0', p))
        self.images = np.array(self.images)
        self.labels = np.array(self.labels)


    def __len__(self):
        return len(self.images)


    def __getitem__(self, idx):
        image_name, label = self.images[idx], self.labels[idx]
        image = cv2.imdecode(np.fromfile(image_name, dtype=np.uint8), -1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))
        image = image / 255.0
        image = np.reshape(image, [3, 224, 224])
        return image, label


    def get_claesses(self):
        return self.labels
