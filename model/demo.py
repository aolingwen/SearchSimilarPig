from pytorch_lightning.utilities.seed import seed_everything
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from model.dolg import DolgNet
from config import Config
import numpy as np
from PIL import Image
from dataset.transform import image_transform
import numpy as np
import faiss
import time
import os
import cv2
import pandas as pd
import torch.nn as nn
import numpy as np
import torchvision.models as models
import torch.nn.functional as F
import torch
import pandas as pd
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

model = DolgNet(
        input_dim=Config.input_dim,
        hidden_dim=Config.hidden_dim,
        output_dim=Config.output_dim,
        num_of_classes=Config.num_of_classes
    )

model = model.load_from_checkpoint('./logs/mymodel-epoch=22-train_loss=0.03.ckpt',
                                   input_dim=Config.input_dim,
                                   hidden_dim=Config.hidden_dim,
                                   output_dim=Config.output_dim,
                                   num_of_classes=Config.num_of_classes).cuda()


SEARCH=True

if SEARCH:
    model.eval()
    img = np.array(Image.open(r'C:\Users\MSI-NB\Desktop\18e13951-4f3a-4bd3-94b9-3e0815ff4887.jpg'))
    img = image_transform(image=img)['image']
    img = img.reshape(1, img.shape[0], img.shape[1], img.shape[2])
    query = model(img.type(torch.cuda.FloatTensor)).cpu().detach().numpy().astype(np.float32).reshape([1,-1])
    query = np.ascontiguousarray(query)

    raw_df = pd.read_excel('./data.xlsx')
    all_path = raw_df['img_path'].values
    all_feature = raw_df.drop(['img_path'], axis=1).values.astype(np.float32)
    all_feature=np.ascontiguousarray(all_feature)

    d = 512                           # 定义向量维度
    nb = len(all_feature)                      # 数据库大小
    nq = 1                       # query数量
    nlist = 5
    k = 10
    quantizer = faiss.IndexFlatIP(d)  # the other index
    index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
    print(index.is_trained)        # 打印index是否训练了
    faiss.normalize_L2(all_feature)
    index.train(all_feature)
    index.add(all_feature)
    print(index.ntotal)            # 打印被构建索引的向量数量

    index.nprobe = 2
    start = time.time()
    D, I = index.search(query, k)     # 真实的search
    print(time.time()-start)

    for i in range(k):
        img = cv2.imdecode(np.fromfile(all_path[I[0][i]], dtype=np.uint8), -1)
        cv2.imshow(str(i), img)
    cv2.waitKey(0)
else:
    model.eval()
    features = []
    df = pd.read_csv('finnal_the_clean.csv')
    img_path = df['id'].values.tolist()
    for p in img_path:
        img = np.array(Image.open(p))
        img = image_transform(image=img)['image']
        img = img.reshape(1, img.shape[0], img.shape[1], img.shape[2])
        feature = model(img.type(torch.cuda.FloatTensor)).cpu().detach().numpy()
        features.append(feature)
    features = np.array(features)

    data = {}
    feature_names = []
    for i in range(512):
        feature_names.append('feature_'+str(i))
    data['img_path'] = img_path
    for i, name in enumerate(feature_names):
        data[name] = features[:,i]
    pd.DataFrame(data).to_excel('./data.xlsx', index=False)

