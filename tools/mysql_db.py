import pymysql


from config import config 
 

class my_mysql:
	
	# 是否正常连接数据库
	def __init__(self):
		self.connect = pymysql.connect(
			host=config.MYSQL_HOST,
			port=config.MYSQL_PORT,
			user=config.MYSQL_USER,
			passwd=config.MYSQL_PASSWD,
			db=config.MYSQL_DB,
			charset='utf8',
			cursorclass = pymysql.cursors.DictCursor )
		self.cursor = self.connect.cursor()
		self.sql = """
				INSERT INTO {}( source, phone, tag, search_list, create_time) 
				VALUES (%s, %s, %s, %s, %s)
				""".format(config.MYSQL_TABLE)


	# 插入一条数据
	def insert_one(self,msg):

		source = msg['source']
		phone = msg['phone']
		tag = msg['tag']
		search_list = '^'.join(msg['search_list'])
		timestamp = msg['timestamp']
		value = (source,phone,tag,search_list,timestamp)

		self.cursor.execute(self.sql,value)
		self.connect.commit()
		return True


	# 插入多条数据
	def insert_many(self,msgs):

		values = []
		for msg in msgs:
			source = msg['source']
			phone = msg['phone']
			tag = msg['tag']
			search_list = '^'.join(msg['search_list'])
			timestamp = msg['timestamp']
			value = (source,phone,tag,search_list,timestamp)
			values.append(value)

		self.cursor.executemany(self.sql,values)
		self.connect.commit()
		return True


	def close(self):
		self.cursor.close()
		self.connect.close()



	# 根据手机号查询一条数据
	def get_one_by_phone(self,phone):

		sql = """
			SELECT * FROM {} WHERE phone='{}'
		""".format(config.MYSQL_TABLE,phone)
		try:
			count = self.cursor.execute(sql)
			if count >0:
				return self.cursor.fetchone()
		except:
			return False



