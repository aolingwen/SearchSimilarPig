#coding:utf8
import os
import requests
import re
import time
import zipfile
from model.dolg_wrapper import DOLGWrapper


import cx_Oracle as cx
import numpy as np


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


class DataLoader:
    def __init__(self, temp_dump_path, data_dump_path):
        self.__oracle_obj = OracleWrapper('ahicquery', 'ahicquery321', '10.0.5.236/ahdbsrv2')
        self.__temp_dump_path = temp_dump_path
        self.__data_dump_path = data_dump_path
        if not os.path.exists(self.__temp_dump_path):
            os.mkdir(self.__temp_dump_path)
        if not os.path.exists(self.__data_dump_path):
            os.mkdir(self.__data_dump_path)
        self.__dolg = DOLGWrapper('')


    '''
    根据日期条件从保险公司内网获取图片并提取图片特征
    '''
    def get_embedding_data(self, begin_date, end_date, riskcode='IPI'):
        # 从orcal数据库中查询符合日期条件的所有保险单号
        registnos = self.__oracle_obj.get_registno(begin_date, end_date, riskcode)
        # 返回的结果
        feature_data = []

        # 根据保险单号获取响应图片
        for no in registnos:
            data = {"format": "xml", "code": "ECM0009",
                    "xml": "<?xml version='1.0' encoding='UTF-8'?><root><BASE_DATA><USER_CODE>0000000000</USER_CODE><USER_NAME>管理员</USER_NAME><ORG_CODE>00000000</ORG_CODE><COM_CODE>00000000</COM_CODE><ORG_NAME>总公司</ORG_NAME><ROLE_CODE>ahsc</ROLE_CODE></BASE_DATA><META_DATA><BATCH><APP_CODE>XYZXLP</APP_CODE><APP_NAME>新养殖险理赔</APP_NAME><BUSI_NO>%s</BUSI_NO></BATCH></META_DATA></root>" %
                           no}
            response = requests.post('http://10.0.0.188:7002/SunECM/servlet/RouterServlet', data=data)
            pat = re.compile('<IMAGE_ZIP_URL>(.*?)</IMAGE_ZIP_URL>')
            data_url = pat.findall(response.text)[0]
            response = requests.get(data_url)
            with open(no + '.zip', 'wb') as f:
                f.write(response.content)

            f = zipfile.ZipFile(no + '.zip', 'r')  # 压缩文件位置
            os.mkdir(no)
            for file in f.namelist():
                f.extract(file, no)  # 解压位置
            f.close()
            os.remove(no + '.zip')
            for p in os.listdir(no):
                pass
        return feature_data




