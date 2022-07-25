#coding:utf8

'''
用于编写搜索功能
'''
from dataloader import DataLoader
from rediswrapper import RedisWrapper
from config import *
import numpy as np
import faiss
import traceback
import time
import datetime

class SearchEngine:
    def __init__(self, logger):
        self.__dataloader = DataLoader(TEST_IMG_DATA_PATH, FILTER_MODEL_MAX_BATCH, logger, DEBUG)
        self.__rediswrapper = RedisWrapper(REDIS_IP, REDIS_PORT)
        self.__logger = logger
        self.__logger.debug("==========begin init search engine===========")
        self.__faiss_index = None
        self.__d = EMBEDDING_SIZE
        self.__nlist = NLIST
        self.__k = K
        self.__nprobe = NPROBE
        raw_data = None
        if DEBUG:
            raw_data = self.__dataloader.get_embedding_data_for_index()
        else:
            now_time = datetime.datetime.now()
            now_time = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
            raw_data = self.__dataloader.get_embedding_data_for_index(START_DATE, now_time)
        features = []
        redis_data = []
        for i, data in enumerate(raw_data):
            features.append(data['feature'])
            tmp = {'registno':data['registno'], 'page_url':data['page_url'], 'id':i}
            redis_data.append(tmp)
        features = np.array(features).astype(np.float32)
        features = np.ascontiguousarray(features)
        quantizer = faiss.IndexFlatIP(self.__d)
        self.__faiss_index = faiss.IndexIVFFlat(quantizer, self.__d, self.__nlist, faiss.METRIC_INNER_PRODUCT)
        faiss.normalize_L2(features)
        self.__faiss_index.train(features)
        self.__faiss_index.add(features)
        print("%d vector has been constructed" % self.__faiss_index.ntotal)
        self.__rediswrapper.delete_all_data()
        self.__rediswrapper.add_data(redis_data)
        print("add data to redis done")
        self.__faiss_index.nprobe = self.__nprobe
        self.__logger.debug("==========search engine init done===========")


    def search(self, registno):
        result = {'result': []}
        self.__logger.debug("==========search begin===========")
        raw_data = self.__dataloader.get_embedding_data_for_query(registno)
        features = []
        pageurls = []
        for i, data in enumerate(raw_data):
            features.append(np.array(data['feature']))
            pageurls.append(data['page_url'])
        query = np.ascontiguousarray(features)
        start = time.time()
        D, I = self.__faiss_index.search(query, 50)
        end = time.time()
        self.__logger.debug('faiss search cost %ss' % str(end - start))
        for i in range(len(I)):
            tmp_data = {'PAGE_URL':pageurls[i], 'result':[]}
            for j, id in enumerate(I[i]):
                result_registno, result_pageurl = self.__rediswrapper.search_registno_by_id(id)
                if result_registno is None or result_pageurl is None:
                    self.__logger.debug("result_registno is None. id is %s" % str(id))
                    break
                if len(tmp_data['result']) < self.__k and result_registno != registno:
                    tmp_result = {'LicenseNo':result_registno, 'CosineSimilarity':float(D[i][j]), 'PAGE_URL':result_pageurl}
                    tmp_data['result'].append(tmp_result)
            result['result'].append(tmp_data)
        self.__logger.debug("==========search end===========")
        return result

    def add_data(self, start_date, end_date):
        data_wait_for_add = []
        result = {'count':0}
        count = 0
        start_index = self.__faiss_index.ntotal
        raw_data = None
        cur_index = start_index

        if DEBUG:
            raw_data = self.__dataloader.get_embedding_data_for_index()
        else:
            raw_data = self.__dataloader.get_embedding_data_for_index(start_date, end_date)
        for data in raw_data:
            registno = data['registno']
            page_url = data['page_url']
            pageurls = self.__rediswrapper.serach_pageids_by_registno(registno)
            if pageurls is None or page_url not in pageurls:
                data_wait_for_add.append({'id':cur_index, 'registno':registno, 'page_url':page_url, 'feature':data['feature']})
                cur_index += 1
        count = cur_index-start_index
        if count > 0:
            self.__rediswrapper.add_data(data_wait_for_add)
            ids = []
            features = []
            for d in data_wait_for_add:
                ids.append(d['id'])
                features.append(d['feature'])
            ids = np.array(ids).astype('int64')
            features = np.array(features).astype(np.float32)
            features = np.ascontiguousarray(features)
            faiss.normalize_L2(features)
            self.__faiss_index.add_with_ids(features, ids)
        result['count'] = count
        return result