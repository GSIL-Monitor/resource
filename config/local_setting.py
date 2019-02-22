# 本地环境配置

DEBUG = True                                                            # 测试环境开启
SQLALCHEMY_ECHO = True                                                  # 把sql语句打印出来
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:bj237237@127.0.0.1/food_db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf-8"                                           # 编码设定
# RELEASE_VERSION = "20190120001"                                       # 不设定版本号，会根据当前时间生成
