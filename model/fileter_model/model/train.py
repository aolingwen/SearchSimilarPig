#coding:utf8

import torch.nn as nn
import torch.optim as optim
from model import FilterNet
from mydataset import MyDataset
import torch
from utils import fit_one_epoch
import torch.backends.cudnn as cudnn

Epoch = 100
Batch_size = 24

train_data = MyDataset('../train/')
val_data = MyDataset('../val/')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


trainloader = torch.utils.data.DataLoader(train_data, batch_size=Batch_size, shuffle=True, pin_memory=True, drop_last=True)
valloader = torch.utils.data.DataLoader(val_data, batch_size=Batch_size, shuffle=False, pin_memory=True, drop_last=True)


model = FilterNet()
model_train = model.train()
if device.type == 'cuda':
    model_train = torch.nn.DataParallel(model)
    cudnn.benchmark = True
    model_train = model_train.cuda()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model_train.parameters(), lr=0.001)
lr_scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.96)

epoch_step = len(train_data)//Batch_size
epoch_step_val = len(val_data)//Batch_size

for epoch in range(Epoch):
    fit_one_epoch(model_train, model, criterion, optimizer, epoch, epoch_step, epoch_step_val, trainloader, valloader, Epoch, True)
    lr_scheduler.step()

