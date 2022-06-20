#coding:utf8

import uvicorn
from fastapi import FastAPI
from dataloader import DataLoader
from config import *
from search_engine import *
from logger import Logger
from rediswrapper import RedisWrapper


if __name__ == "__main__":
    log = Logger(LOG_PATH)
    # 数据加载器
    dataloader = DataLoader(TEST_IMG_DATA_PATH, FILTER_MODEL_MAX_BATCH, log, True)
    print(dataloader.get_embedding_data_for_query('RIPI202021010600000075'))
















