# 生产环境配置

DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Xingge@123456@127.0.0.1/resource?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"

APP = {
    'domain': 'http://resource.hikiwi.cn'
}

RELEASE_VERSION = "20190222001"