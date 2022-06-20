#coding:utf8
import os
import time
import requests
import re
import zipfile
from model.dolg_wrapper import DOLGWrapper
from model.filter_wrapper import FilterWrapper
import math
import cx_Oracle as cx
import numpy as np
from utils import *
import traceback
import shutil
import torch

# Oracle的封装，外部不会主动调用
class OracleWrapper:
    def __init__(self, user, passwd, dsn):
        self.__conn = cx.connect(user, passwd, dsn)

    '''
    根据日期条件获取保险单号
    '''
    def get_registno(self, begin_date, end_date, riskcode='IPI'):
        cursor = self.__conn.cursor()
        cursor.execute("select registno from business.prplclaim a where a.riskcode='%s' and a.claimdate>=to_date('%s','yyyy-mm-dd hh24:mi:ss') and a.claimdate<=to_date('%s','yyyy-mm-dd hh24:mi:ss')" % (riskcode, begin_date, end_date))
        result = cursor.fetchall()
        cursor.close()
        result = np.array(result).reshape([-1]).tolist()
        return result

    def __del__(self):
        self.__conn.close()

# 数据加载器
class DataLoader:
    def __init__(self, test_data_path, max_batch, logger, debug=True):
        self.__logger = logger
        self.__max_batch = max_batch
        self.__debug = debug
        if self.__debug is False:
            self.__oracle_obj = OracleWrapper('ahicquery', 'ahicquery321', '10.0.5.236/ahdbsrv2')
        self.__test_data_path = test_data_path
        if self.__debug:
            if not os.path.exists(self.__test_data_path):
                os.mkdir(self.__test_data_path)
        self.__dolg = DOLGWrapper('./model/logs/mymodel-epoch=53-train_loss=0.02.ckpt')
        flag = torch.cuda.is_available()
        self.__filter = FilterWrapper('./model/logs/ep015-loss0.031-val_loss0.059.pth', flag)


    def get_embedding_data_for_query(self, registno):
        '''
        根据保单号，获取待查询的数据
        若debug为True则在test_data中寻找名字为registno的目录
        若debug为False则通过发送请求的方式获取数据
        :param registno: 保险单号
        :return: ndarray  [-1, 512]
        '''
        feature_data = []
        if self.__debug:
            if os.path.exists(os.path.join(self.__test_data_path, registno)):
                start = time.time()
                interested_img_path, page_ids = parse_xml(os.path.join(self.__test_data_path, registno, 'busi.xml'))
                for i in range(len(interested_img_path)):
                    interested_img_path[i] = os.path.join(self.__test_data_path, registno, interested_img_path[i])
                output = []
                for i in range(0, int(math.ceil(len(interested_img_path)/self.__max_batch))):
                    temp_output = self.__filter.predict(interested_img_path[i*self.__max_batch:(i+1)*self.__max_batch]).tolist()
                    output.extend(temp_output)
                for i, o in enumerate(output):
                    if o == 1:
                        feature = self.__dolg.embedding(interested_img_path[i])
                        feature_data.append({'registno':registno, 'feature':feature, 'page_id':page_ids[i]})
                end = time.time()
                self.__logger.debug('get_embedding_data_for_query() cost %ss' % str(end-start))
        else:
            data = {"format": "xml", "code": "ECM0009",
                    "xml": "<?xml version='1.0' encoding='UTF-8'?><root><BASE_DATA><USER_CODE>0000000000</USER_CODE><USER_NAME>管理员</USER_NAME><ORG_CODE>00000000</ORG_CODE><COM_CODE>00000000</COM_CODE><ORG_NAME>总公司</ORG_NAME><ROLE_CODE>ahsc</ROLE_CODE></BASE_DATA><META_DATA><BATCH><APP_CODE>XYZXLP</APP_CODE><APP_NAME>新养殖险理赔</APP_NAME><BUSI_NO>%s</BUSI_NO></BATCH></META_DATA></root>" %
                           registno}
            response = requests.post('http://10.0.0.188:7002/SunECM/servlet/RouterServlet', data=data)
            pat = re.compile('<IMAGE_ZIP_URL>(.*?)</IMAGE_ZIP_URL>')
            data_url = pat.findall(response.text)[0]
            try:
                response = requests.get(data_url)
                with open(os.path.join('./', registno + '.zip'), 'wb') as f:
                    f.write(response.content)
                f = zipfile.ZipFile(os.path.join('./', registno + '.zip'), 'r')  # 压缩文件位置
                if not os.path.exists(os.path.join('./', registno)):
                    os.mkdir(os.path.join('./', registno))
                for file in f.namelist():
                    f.extract(file, os.path.join('./', registno))  # 解压位置
                f.close()
                os.remove(os.path.join('./', registno + '.zip'))
                start = time.time()
                interested_img_path, page_ids = parse_xml(os.path.join('./', registno, 'busi.xml'))
                for i in range(len(interested_img_path)):
                    interested_img_path[i] = os.path.join(self.__test_data_path, registno, interested_img_path[i])
                output = []
                for i in range(0, int(math.ceil(len(interested_img_path)/self.__max_batch))):
                    temp_output = self.__filter.predict(interested_img_path[i*self.__max_batch:(i+1)*self.__max_batch]).tolist()
                    output.extend(temp_output)
                for i, o in enumerate(output):
                    if o == 1:
                        feature = self.__dolg.embedding(interested_img_path[i])
                        feature_data.append({'registno': registno, 'feature': feature, 'page_id': page_ids[i]})
                end = time.time()
                self.__logger.debug('get_embedding_data_for_query() cost %ss' % str(end - start))
                shutil.rmtree(os.path.join('./', registno))
            except Exception as e:
                self.__logger.error(traceback.format_exc())
                if os.path.exists(os.path.join('./', registno)):
                    shutil.rmtree(os.path.join('./', registno))
                raise e
        return feature_data

    def get_embedding_data_for_index(self, begin_date=None, end_date=None, riskcode='IPI'):
        '''
        若debug为True，则从test_data中批量提取对应保单的图片特征，用于入库建索引
        若debug为False，则从安华内网根据日期条件批量查询保单号，并根据保单号获取数据的特征，用于入库建索引
        :param begin_date: 起始日期，若debug为True，则忽略
        :param end_date: 截止日期，若debug为True，则忽略
        :param riskcode: 保险种类id，默认IPI
        :return:  [{'registno':'RIPI202021010600000078', 'feature':[0.255,0235..,,..], 'page_id': ['adsfasdfww', 'adsfasdfww']}, {'registno':'RIPI202021010600000079', 'feature':[0.255,0235..,,..], 'page_id': ['adsfasdfww', 'adsfasdfww']}]
        '''
        # 返回的结果
        feature_data = []

        if self.__debug == False:
            # 从orcal数据库中查询符合日期条件的所有保险单号
            registnos = self.__oracle_obj.get_registno(begin_date, end_date, riskcode)
            # 根据保险单号获取响应图片
            for no in registnos:
                data = {"format": "xml", "code": "ECM0009",
                        "xml": "<?xml version='1.0' encoding='UTF-8'?><root><BASE_DATA><USER_CODE>0000000000</USER_CODE><USER_NAME>管理员</USER_NAME><ORG_CODE>00000000</ORG_CODE><COM_CODE>00000000</COM_CODE><ORG_NAME>总公司</ORG_NAME><ROLE_CODE>ahsc</ROLE_CODE></BASE_DATA><META_DATA><BATCH><APP_CODE>XYZXLP</APP_CODE><APP_NAME>新养殖险理赔</APP_NAME><BUSI_NO>%s</BUSI_NO></BATCH></META_DATA></root>" %
                               no}
                response = requests.post('http://10.0.0.188:7002/SunECM/servlet/RouterServlet', data=data)
                pat = re.compile('<IMAGE_ZIP_URL>(.*?)</IMAGE_ZIP_URL>')
                data_url = pat.findall(response.text)[0]
                try:
                    response = requests.get(data_url)
                    with open(os.path.join('./', no + '.zip'), 'wb') as f:
                        f.write(response.content)

                    f = zipfile.ZipFile(os.path.join('./', no + '.zip'), 'r')  # 压缩文件位置
                    if not os.path.exists(os.path.join('./', no)):
                        os.mkdir(os.path.join('./', no))
                    for file in f.namelist():
                        f.extract(file, os.path.join('./', no))  # 解压位置
                    f.close()
                    os.remove(os.path.join('./', no + '.zip'))
                    start = time.time()
                    interested_img_path, page_ids = parse_xml(os.path.join('./', no, 'busi.xml'))
                    for i in range(len(interested_img_path)):
                        interested_img_path[i] = os.path.join(self.__test_data_path, no, interested_img_path[i])
                    output = []
                    for i in range(0, int(math.ceil(len(interested_img_path) / self.__max_batch))):
                        temp_output = self.__filter.predict(
                            interested_img_path[i * self.__max_batch:(i + 1) * self.__max_batch]).tolist()
                        output.extend(temp_output)
                    for i, o in enumerate(output):
                        if o == 1:
                            feature = self.__dolg.embedding(interested_img_path[i])
                            feature_data.append({'registno': no, 'feature': feature, 'page_id': page_ids[i]})
                    end = time.time()
                    self.__logger.debug('get_embedding_data_for_query() cost %ss' % str(end - start))
                    shutil.rmtree(os.path.join('./', no))
                except Exception as e:
                    self.__logger.error(traceback.format_exc())
                    if os.path.exists(os.path.join('./', no)):
                        shutil.rmtree(os.path.join('./', no))
                    raise e
        else:
            for registno in os.listdir(self.__test_data_path):
                interested_img_path, page_ids = parse_xml(os.path.join(self.__test_data_path, registno, 'busi.xml'))
                for i in range(len(interested_img_path)):
                    interested_img_path[i] = os.path.join(self.__test_data_path, registno, interested_img_path[i])
                output = []
                for i in range(0, int(math.ceil(len(interested_img_path)/self.__max_batch))):
                    temp_output = self.__filter.predict(interested_img_path[i*self.__max_batch:(i+1)*self.__max_batch]).tolist()
                    output.extend(temp_output)
                for i, o in enumerate(output):
                    if o == 1:
                        feature = self.__dolg.embedding(interested_img_path[i])
                        feature_data.append({'registno': registno, 'feature': feature, 'page_id': page_ids[i]})
        return feature_data

