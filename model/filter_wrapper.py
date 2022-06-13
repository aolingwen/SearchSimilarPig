import torch
from model.fileter_model.model.model import FilterNet
import torch.backends.cudnn as cudnn
import cv2
import numpy as np

class FilterWrapper:
    def __init__(self, model_path, cuda=True):
        self.cuda = cuda
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = FilterNet()
        model.load_state_dict(torch.load(model_path, map_location=device))
        self.net = model.eval()
        print('{} model loaded.'.format(model_path))

        if cuda:
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = True
            self.net = self.net.cuda()


    def predict(self, paths):
        images = []
        for p in paths:
            image = cv2.imdecode(np.fromfile(p, dtype=np.uint8), -1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (224, 224))
            image = image / 255.0
            images.append(image)
        images = np.reshape(images, [-1, 3, 224, 224])
        with torch.no_grad():
            images = torch.from_numpy(images).type(torch.FloatTensor)
            if self.cuda:
                images = images.cuda()
            # ---------------------------------------------------#
            #   获得预测结果，output输出为概率
            # ---------------------------------------------------#
            output = self.net(images)
            output = torch.nn.Softmax()(output)
            output = torch.argmax(output, axis=1)
        return output
