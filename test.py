import requests
import time


def get_proxies(num=1):
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


url = 'http://www.baidu.com/'
proxies = get_proxies()
print(proxies)
a = time.time()
print(requests.get(url,proxies=proxies).text)
print(time.time()-a)


import sys
print(sys.path)