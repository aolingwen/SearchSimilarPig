#coding:utf8

import torch.nn as nn
import numpy as np
import torchvision.models as models
import torch.nn.functional as F
import torch

class FilterNet(nn.Module):
    def __init__(self):
        super(FilterNet, self).__init__()
        self.resnet_pretrained = models.densenet121(pretrained=True)
        self.fc1 = nn.Linear(1000, 100)
        self.fc2 = nn.Linear(100, 2)

    def forward(self, x):
        out = self.resnet_pretrained(x)
        out = F.relu(self.fc1(out))
        out = self.fc2(out)
        return out


if __name__ == "__main__":
    net = FilterNet()
    data = np.random.normal(size=(1, 3, 360, 120))
    data = torch.FloatTensor(data)
    print(net(data))