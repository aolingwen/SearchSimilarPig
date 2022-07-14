#coding:utf8

'''
用于编写配置
'''
#日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": '%(asctime)s - %(levelprefix)s %(filename)s --- %(message)s',
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./logs.txt"
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./logs.txt"

        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
#oracle账号
ORACLE_USER = 'ahicquery'
#oracle密码
ORACLE_PASSWORD = 'ahicquery321'
#oracle dsn
ORACLE_DSN = '10.0.5.236/ahdbsrv2'
#拿图的url
IMGDATA_URL = 'http://10.0.0.188:7002/SunECM/servlet/RouterServlet'
#是否处于调试状态
DEBUG = False
#测试数据的根目录
TEST_IMG_DATA_PATH = './test_data'
#日志目录
LOG_PATH = './logs.txt'
#过滤器模型最大BATCH数量
FILTER_MODEL_MAX_BATCH = 8
#redis IP
REDIS_IP='127.0.0.1'
#redis 端口
REDIS_PORT=6379
#embedding size
EMBEDDING_SIZE=512
#聚类类别数量
NLIST = 8
#TOP K
K = 5
#nprobe
NPROBE = 2
#初始化时加载数据的起始日期
START_DATE = '2022-07-14 18:20:00'

