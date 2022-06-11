#coding:utf8

import sys
import os
import logging


class Logger(object):
    """
    日志处理类
    """
    def __init__(self, path, level=logging.DEBUG):
        """
        :param path: 日志路径
        :param level: 日志打印级别
        """
        # 创建一个日志器logger并设置其日志级别为DEBUG
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个日志器logger并设置其日志级别为DEBUG
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # 创建一个格式器formatter并将其添加到处理器handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        handler.setFormatter(formatter)

        # 为日志器logger添加上面创建的处理器handler
        self.logger.addHandler(handler)

        # 设置文件日志
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        """
        :param message: debug信息
        :return:
        """
        self.logger.debug(message)

    def info(self, message):
        """
        :param message: info信息
        :return:
        """
        self.logger.info(message)

    def warn(self, message):
        """
        :param warn: warn 信息
        :return:
        """
        self.logger.warn(message)

    def critical(self, message):
        """
        :param message: critical 信息
        :return:
        """
        self.logger.critical(message)

    def error(self, message):
        """
        :param message: error 信息
        :return:
        """
        self.logger.error(message)