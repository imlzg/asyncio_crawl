import redis
import pickle

from config import config


class CookieReids(object):

    R = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,db=0,password=config.REDIS_PWD)
    P = R.pipeline(transaction=False)

    def put_one(self,value):
        if not isinstance(value,dict):
            return
        return self.R.sadd(config.COOKIE_REDIS_SET_NAME,pickle.dumps(value))

    def get_one(self):
        ext = self.R.spop(config.COOKIE_REDIS_SET_NAME)
        return pickle.loads(ext) if ext else None

    def get_many(self):
        try:
            [self.P.spop(config.COOKIE_REDIS_SET_NAME) for x in range(config.COOKIE_GET_SIZE)]
            return list(map(lambda x: pickle.loads(x),self.P.execute()))
        except Exception as e:
            return []

    def cookie_count(self):
        return self.R.scard(config.COOKIE_REDIS_SET_NAME)



class PhoneRedis(object):
    """保存生成号码的类"""

    R = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,db=1,password=config.REDIS_PWD)
    P = R.pipeline(transaction=False)

    def put_one(self,phone):
        return self.R.sadd(config.PHONE_REDIS_SET_NAME, phone)

    def get_one(self):
        return self.R.spop(config.PHONE_REDIS_SET_NAME)

    def put_many(self,phones): 
        for phone in phones:
            self.P.sadd(config.PHONE_REDIS_SET_NAME,phone)
        return self.P.execute()
        
    def get_many(self):
        try:
            [self.P.spop(config.PHONE_REDIS_SET_NAME) for x in range(config.PHONE_GET_SIZE)]
            return self.P.execute()
        except:
            return []

    def get_count(self):
        return self.R.scard(config.PHONE_REDIS_SET_NAME)



class RecordRedis:

    """保存号码生成记录的类"""
    R = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,db=2,password=config.REDIS_PWD)

    def write(self,record):
        return self.R.set('record',record)

    def read(self):
        try:
            return int(self.R.get('record').decode('utf-8'))
        except:
            return 0



cookie_redis = CookieReids() 
phone_redis = PhoneRedis()
record_redis = RecordRedis()


