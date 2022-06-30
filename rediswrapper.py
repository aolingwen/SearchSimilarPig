#coding:utf8

import os
import redis
import json

class RedisWrapper:
    def __init__(self, redis_ip, redis_port):
        '''
        :param redis_ip: redis的ip
        :param redis_port: redis的端口
        '''
        self.__pool = redis.ConnectionPool(host=redis_ip, port=redis_port, decode_responses=True)
        self.__faiss_prefix = 'SearchSimilarImages:KVStore:FaissID2RegistNO:'
        self.__registno_prefix = 'SearchSimilarImages:KVStore:RegistNO2PageIDS:'


    def delete_all_data(self):
        conn = redis.Redis(connection_pool=self.__pool)
        for elem in conn.keys("SearchSimilarImages:KVStore:FaissID2RegistNO*"):
            conn.delete(elem)
        for elem in conn.keys("SearchSimilarImages:KVStore:RegistNO2PageIDS*"):
            conn.delete(elem)


    def add_data(self, data):
        '''
        将data写入redis，data需要是个列表
        :param data:[{'id':123, 'registno':'RIPI202021010700000068', 'page_id':'1040a4f1705441398dcfb3b7d09835f2'},
        {'id':124, 'registno':'RIPI202021010700000069', 'page_id':'2040a4f1705441398dcfb3b7d09835f2'}]
        :return: None
        '''
        conn = redis.Redis(connection_pool=self.__pool)
        for d in data:
            id = d['id']
            registno = d['registno']
            page_id = d['page_id']
            conn.set(self.__faiss_prefix+str(id), registno)
            conn.lpush(self.__registno_prefix+registno, page_id)

    def search_registno_by_id(self, id):
        '''
        根据faiss id查找对应的保险单号
        :param id:faiss id
        :return:保险单号，如果查不到则会返回None
        '''
        conn = redis.Redis(connection_pool=self.__pool)
        return conn.get(self.__faiss_prefix+str(id))

    def serach_pageids_by_registno(self, registno):
        '''
        根据保险单号查找对应的所有pageid
        :param registno: 保险单号
        :return: pageid列表，如果查不到则会返回None
        '''
        page_ids = []
        conn = redis.Redis(connection_pool=self.__pool)
        for page_id in conn.lrange(self.__registno_prefix+registno, 0, -1):
            page_ids.append(page_id)
        if len(page_ids) == 0:
            return None
        return page_ids


if __name__=='__main__':
    redis_obj = RedisWrapper('127.0.0.1', 6379)
    data = [{'id':123, 'registno':'RIPI202021010700000068', 'pageids':['1040a4f1705441398dcfb3b7d09835f2',
        '0b317c05cd6c4db894dc8c00e924d802', 'a4a40a3f089e4c50b834a5233b2f7838']},
        {'id':124, 'registno':'RIPI202021010700000069', 'pageids':['2040a4f1705441398dcfb3b7d09835f2',
        '0b317c05cd6c4db894dc8c00e924d801', 'a4a40a3f089e4c50b834a5233b2f7839']}]
    redis_obj.add_data(data)
    print(redis_obj.search_registno_by_id(123))
    print(redis_obj.serach_pageids_by_registno('RIPI202021010700000068'))
