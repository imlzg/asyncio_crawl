import os
import re
import time
import copy
import asyncio

import aiohttp
from aiohttp import ClientSession 
from lxml import etree

from config import config
from tools.mysql_db import my_mysql
from tools.redis_db import cookie_redis
from tools.tool import get_current_timestamp, get_phones, get_logger


# 根据配置限定并发的数量，+2是为了额外的协程保证cookie，phone

# 获取日志对象
DISTRIBUTE_LOGER = get_logger('distribute')  

# 从机本地cookie池 和 手机号池
COOKIES = []
PHONES = []
# 正在使用的cookie
COOKIE = None
# 记录获取了多少cookie，phone
P_COUNT =1000
C_COUNT = 10
# 记录查询成功了多少标签
R_COUNT = 0

# 爬取需要的 参数 header，cookie，代理
NAME = 'sougou'
HEADERS = {
"Host":"www.sogou.com",
"Connection":"keep-alive",
"User-Agent":("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) App"
	"leWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"),
"Accept":"*/*",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
}

# 用于入库
RESS = []
# 缓存结果超过50条开始入库
RESS_LEN = 20


def prestrain_cookie_phone():
	"""
		预装手机号，cookie
	"""
	global COOKIES,PHONES
	while not COOKIES:
		DISTRIBUTE_LOGER.debug('-- feed cookie first --')
		COOKIES = cookie_redis.get_many()
	while  not PHONES:
		DISTRIBUTE_LOGER.debug('-- feed phone first --')
		PHONES = get_phones()


def flush_cookie():
	"""
		从本地cookie池获取一个可用cookies
	"""
	global COOKIE
	if COOKIES:
		COOKIE = COOKIES.pop()
	else:
		asyncio.sleep(1)


async def ensure_cookies():
	"""
		不断从redis获取cookie，确保从机cooKie池有一定数量的cookie
	"""
	global C_COUNT
	while 1:
		if len(COOKIES) < config.COOKIE_LIST_SIZE:
			cookies = cookie_redis.get_many()
			if not cookies:
				DISTRIBUTE_LOGER.warning('001 redis no cookie to get -------------')
				continue
			C_COUNT += config.COOKIE_GET_SIZE
			DISTRIBUTE_LOGER.debug('get {} cookies from redis, total get {}'.format(config.COOKIE_GET_SIZE,C_COUNT))
			COOKIES.extend(cookies)
		await asyncio.sleep(1)


async def ensure_phones():
	"""
		不断从redis获取phone block，确保从机号码池有一定数量的号码
	"""
	global P_COUNT
	while 1:
		if len(PHONES) < config.PHONE_LIST_SIZE:
			phones = get_phones()
			if not phones:
				DISTRIBUTE_LOGER.warning('002 redis no phone to get ------------')
				continue
			P_COUNT += config.PHONE_GET_SIZE*100
			DISTRIBUTE_LOGER.debug('get {} phones from redis, total get {}'.format(config.PHONE_GET_SIZE*100,P_COUNT))
			PHONES.extend(phones)
		await asyncio.sleep(1)


async def ensure_res():
	"""
		本地缓存结果达到一定数目向mysql入库
	"""
	global RESS, R_COUNT
	while 1:
		if len(RESS) > RESS_LEN:
			con = copy.deepcopy(RESS)
			RESS = []
			retry = 5
			while retry:
				try:
					mysql_obj = my_mysql()
					mysql_obj.insert_many(con)
					mysql_obj.close()
					lens = len(con)
					R_COUNT += lens
					DISTRIBUTE_LOGER.debug('send {} res to mysql, total send {}'.format(lens,R_COUNT))
					break
				except Exception as e:
					retry -= 1
					DISTRIBUTE_LOGER.warning('003 not insert to mysql,insert again {}-----------'.format(retry))
					if not retry:
						DISTRIBUTE_LOGER.warning(con)
						DISTRIBUTE_LOGER.warning(e)
						break
		await asyncio.sleep(1)


async def get_tag_in_web(phone):
	"""
		在搜狗的web页面给号码打标签
	"""
	url = 'https://www.sogou.com/web?query={}'.format(phone)
	while 1:
		cookie_now = COOKIE
		try:
			async with ClientSession() as client:
				async with client.get(url,headers=HEADERS,cookies=COOKIE) as res:
					resp = await res.text()
			# cookie过期，刷新cookie重试
			if ' <form name="authform" method="POST" id="seccodeForm" action="/">' in resp \
			or 'sogou.com";"snapshot.sogoucdn.com"' in resp: 
				# cookies 已经刷新过了就不刷新cookie
				if cookie_now == COOKIE:
					flush_cookie()
				continue
			break
		except Exception as e:
			# 下载失败，重试
			continue

	xml = etree.HTML(resp)
	# 获取若干个搜索结果
	search = xml.xpath("//div[@class='results']/div/h3/a")
	search_list = list(map(lambda x:x.xpath('string(.)').strip(),search))
	try:
		info_list = search_list[:config.sougou_search_num]
	except:
		info_list = search_list

	# 是号码的第1种情况
	try:
		msg = re.search(r'号码通用户数据：(.*?)\)',resp).group(1).replace(
				"','0','5','",'')
		return (msg,info_list,'搜狗号码通')
	except Exception as e:
		pass

	# 是号码的第2种情况
	try:
		a_list = xml.xpath("//div[@class='rb']/h3/a")
		for a in a_list:
			if 'sogou_vr_70030302_title' in a.xpath('./@id')[0]:
				return (a.xpath('./text()')[0],info_list,'搜狗')
	except Exception as e:
		pass

	#未搜到的情况	
	return ('error mobile',info_list,'')


async def query():
	while 1:
		phone = PHONES.pop()
		# 查询归属地 和 号码标签
		tag, info_list, source = await get_tag_in_web(phone)
		res = {
		'source':source,
		'phone':phone,
		'tag':tag.replace('：0',':').replace("'",''),
		'search_list':info_list,
		'timestamp':get_current_timestamp()}

		# 一般有便签都有 :
		if ':' in res['tag']:
			RESS.append(res)



def main():

	loop = asyncio.get_event_loop()
	# 预装cookie phone
	prestrain_cookie_phone()
	DISTRIBUTE_LOGER.debug(' ##### start crawl with worker {} #####'.format(config.WORKER_NUM))
	# cookie 
	asyncio.ensure_future(ensure_cookies())
	# # phone
	asyncio.ensure_future(ensure_phones())	
	# # res 
	asyncio.ensure_future(ensure_res())	

	for i in range(100):
		asyncio.ensure_future(query())

	try:
		loop.run_forever()
	except KeyboardInterrupt:
	    pass
	finally:
	    print("close Loop")
	    loop.close()







if __name__ == '__main__':
	main()




