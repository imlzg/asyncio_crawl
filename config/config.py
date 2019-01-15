
# --- mysql 配置
# mysql host
MYSQL_HOST = ''
# msql prot 
MYSQL_PORT = 3306
# 用户名
MYSQL_USER = "phone_tag" 
# 密码
MYSQL_PASSWD = "Tianli2018"   
# 数据库   
MYSQL_DB =  "phone_tag"  
# 表名
MYSQL_TABLE = 'phone_tag'  


# -- redis 配置
# redis 地址
REDIS_HOST = ''
# redis 端口
REDIS_PORT = 6379
# redis 密码
REDIS_PWD = 'tianli2018'
# redis cookie 集合名  
COOKIE_REDIS_SET_NAME = 'cookiejars' 
# cookie 池的大小  
COOKIES_POOL_SIZE = 10000
# redis phone 集合名
PHONE_REDIS_SET_NAME = 'phone'    
# 号码池的大小
PHONE_POOL_SIZE = 1000000

# salve 号码缓存数目
PHONE_LIST_SIZE = 1000
# slave 一次获取的号码段数目
PHONE_GET_SIZE  = 10
# slave cookie缓存数目
COOKIE_LIST_SIZE = 10
# slave 一次获取cookie的数目
COOKIE_GET_SIZE = 10


# ---selenium chrome 配置
# chrome driver的目录
CHROME_DRIVER_PATH = '/Users/apple/phantomjs-2.1.1-macosx/bin/chromedriver'
# driver 首次打开的地址
CHROME_BASE_URL = "https://www.sogou.com/"



# --- kafka配置
#卡夫卡 group id
KAFKA_GROUP_ID = 'data'
#卡夫卡 ips
KAFKA_IPS = []
# 卡夫卡搜狗cookies topic
KAFKA_SOUGOU_COOKIE_TOPIC = 'sougou_cookie'
# 卡夫卡搜狗电话号段topic
KAFKA_SOUGOU_PHONE_TOPIC = 'sougou_phone'


# download
# 全局下载超时时间 秒
TIMEOUT = 2
# 全局下载重试次数
RETRY = 2
#搜狗获取保存的搜索条数
sougou_search_num = 5
# 并发，协程数量
WORKER_NUM = 70


# 日志设置
LOG_DIR = 'log'
LOG_SIZE = 10
LOG_BACKUP = 5

