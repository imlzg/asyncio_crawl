import gevent
from kafka import KafkaProducer,KafkaConsumer

from config import config



class KafSend:
	"""和卡夫卡保持连接生产数据"""

	def is_connected(self):
		try:
			with gevent.Timeout(5):
				self.producer = KafkaProducer(bootstrap_servers=config.KAFKA_IPS) 
			return True 
		except Exception as e:
			print(e)

	def send(self,topic,value):
		try:
			value = value.encode('utf-8')
			self.producer.send(topic,value=value)
		except Exception as e:
			print(e)

	def send_many(self,topic,values):
		for value in values:
			self.send(topic,value)


class KafRecv:
	"""和卡夫卡保持连接获取数据"""

	def is_connected(self):
		try:
			consumer = KafkaConsumer(
							 group_id=config.KAFKA_GROUP_ID,
							 bootstrap_servers=config.KAFKA_IPS,
							 consumer_timeout_ms=1000,
							 ) 
			self.consumer = consumer
			return True
		except Exception as e:
			print(e)
			return False

	def get(self,topic):
		return self.consumer.subscribe(topic)   


def get_many_from_kaf(topic,num):
	"""从卡夫卡一次性获取一定量的数据，不保持连接"""
	try:
		consumer = KafkaConsumer(
						 group_id=config.KAFKA_GROUP_ID,
						 bootstrap_servers=config.KAFKA_IPS,
						 max_poll_records=num,
						 ) 
		consumer.subscribe(topic)
		res = consumer.poll(timeout_ms=1000, max_records=num)
	except Exception as e:
		print(e)
		res = {}
	finally:
		try:
			consumer.close()
		except:
			pass
	return res






