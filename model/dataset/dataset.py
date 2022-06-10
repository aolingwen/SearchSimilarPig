import os
import pandas as pd
from sklearn import preprocessing
from torch.utils.data import Dataset
from model.dataset.transform import image_transform
from model.config import Config
from PIL import Image
import numpy as np
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class LmkRetrDataset(Dataset):
    def __init__(self):
        self.df = pd.read_csv(Config.CSV_PATH)
        self.landmark_id_encoder = preprocessing.LabelEncoder()
        self.df['landmark_id'] = self.landmark_id_encoder.fit_transform(self.df['landmark_id'])
        self.df['path'] = self.df['id']
        self.paths = self.df['path'].values
        self.ids = self.df['id'].values
        self.landmark_ids = self.df['landmark_id'].values
        self.transform = image_transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        path, id, landmark_id = self.paths[idx], self.ids[idx], self.landmark_ids[idx]
        # img = jpeg.JPEG(path).decode()
        img = np.array(Image.open(path))
        if self.transform:
            img = self.transform(image=img)['image']
        return img, landmark_id, id
