import os
import time
import logging
from logging.handlers import RotatingFileHandler

import requests
requests.packages.urllib3.disable_warnings()

from config import config
from tools.redis_db import phone_redis


def get_current_timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
 

def get_phone():
    con = phone_redis.get_many()
    if not con:
        return []
    return list(map(lambda x:int(x),con))


def get_phones():
    phones = []
    phone_con = get_phone()
    for _ in phone_con:
        for phone in range(_,_+100):
            phones.append(phone)
    return phones


def back_phone(phone):   
    pass


def get_proxies():
    """获取可用的代理ip"""
    try:
        url = 'http://182.92.254.9:8210/v1/proxy/obtain/?crawl_carrier={}'.format(num)
        proxies_list = requests.get(url).json()['proxies']
        proxies={
            'http':proxies_list[0],
            'https':proxies_list[0]
        }
        return proxies
    except:
        return None


def ensure_dir(fname):
    if fname.endswith(os.sep):
        fname = fname.rstrip(os.sep)
    fname = os.path.dirname(fname)
    dirs = fname.split(os.sep)
    for i in range(len(dirs)):
        d = os.sep.join(dirs[:i + 1])
        if not os.path.isdir(d):
            try:
                os.mkdir(d)
            except Exception as e:
                pass


def get_log_file_name(fname, log_dir=config.LOG_DIR):
    """获取log的文件名"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), log_dir, fname + '.log')


def get_logger(name):
    """获取loger对象"""
    fname = get_log_file_name(name)
    ensure_dir(fname)
    api_logger = logging.getLogger(fname)

    # 打印日志
    steam_handler = logging.StreamHandler()
    # 写入日志
    rotating_handler = RotatingFileHandler(
        fname, maxBytes=config.LOG_SIZE * 1024 * 1024, backupCount=config.LOG_BACKUP)
    # 每行日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s')
    rotating_handler.setFormatter(formatter)
    steam_handler.setFormatter(formatter)
    api_logger.addHandler(rotating_handler)
    api_logger.addHandler(steam_handler)
    # 设置日志处理级别
    api_logger.setLevel(logging.DEBUG)
    return api_logger





   
