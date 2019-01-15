import time
import requests
from lxml import etree


from config import config
from tools.tool import get_current_timestamp
from tools.mysql_db import my_mysql

NAME = 'baidu'

headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'no-cache',
	'Connection': 'keep-alive',
	'Host': 'www.baidu.com',
	'Pragma': 'no-cache',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}


def get_content(phone):
	try:
		res = requests.get(f'https://www.baidu.com/s?wd={phone}', headers=headers)
		reshtml = etree.HTML(res.text)

		# tag addr
		content = reshtml.xpath(".//div[@class='result-op c-container']//div"
							"[@class='c-span21 c-span-last']//span//text()")[1]
		con_list = content.split("  ")
		if len(con_list) > 1:
			addr = ''.join(con_list[0].split())
			tag = con_list[1]
		else:
			addr = ''
			tag = con_list[0]

		# info_list
		try:
			search = reshtml.xpath("//div[@class='result c-container ']/h3/a/text()")
			info_list = search[:config.sougou_search_num]
		except:
			info_list = search

		# package
		msg = {
			'source':NAME,
			'phone': phone,
			'status': 'success',
			'addr': addr,
			'tag': tag,
			'search_list':info_list,
			'timestamp': get_current_timestamp()
		}

		# 按要求入库
		if 1:
			mysql_obj.save_to_db(msg)

		return msg
	except Exception as e:
		return {
			'source':NAME,
			'phone': phone,
			'status': 'failed',
			't': get_current_timestamp()
		}


if __name__ == '__main__':
	phone  = '114'
	print(get_content(phone))
