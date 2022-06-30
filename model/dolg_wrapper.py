#condig:utf8

from model.model.dolg import DolgNet
import numpy as np
from PIL import Image
from model.dataset.transform import image_transform
from model.config import Config
import torch


class DOLGWrapper:
    def __init__(self, model_path):
        self.model = DolgNet(input_dim=Config.input_dim,hidden_dim=Config.hidden_dim,output_dim=Config.output_dim,num_of_classes=Config.num_of_classes)
        self.model = self.model.load_from_checkpoint(model_path,
                                           input_dim=Config.input_dim,
                                           hidden_dim=Config.hidden_dim,
                                           output_dim=Config.output_dim,
                                           num_of_classes=Config.num_of_classes)
        if torch.cuda.is_available():
            self.model = self.model.cuda()

    def embedding(self, img_path):
        img = np.array(Image.open(img_path))
        img = image_transform(image=img)['image']
        img = img.reshape(1, img.shape[0], img.shape[1], img.shape[2])
        flag = torch.cuda.is_available()
        if flag:
            query = self.model(img.type(torch.cuda.FloatTensor)).cpu().detach().numpy().astype(np.float32).reshape([-1])
        else:
            query = self.model(img.type(torch.FloatTensor)).cpu().detach().numpy().astype(np.float32).reshape([-1])
        query = np.ascontiguousarray(query)
        return query