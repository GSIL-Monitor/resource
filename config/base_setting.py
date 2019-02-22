# 共用配置文件

SERVER_PORT = 5000
DEBUG = False               # 默认不开启
SQLALCHEMY_ECHO = False     # 默认不开启，把sql语句打印出来

AUTH_COOKIE_NAME = "alien_food"  # 定义cookie name

# 过滤url,这些页面不需要判断登录状态
IGNORE_URLS = [
    "^/user/login"
]
IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]
API_IGNORE_URLS = [
    "^/api"                     # 微信小程序接口不作登录过滤
]

# 分页(每一页显示多少)
PAGE_SIZE = 50

# 显示10页
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

# 小程序配置文件
MINA_APP = {
    "appid": "wx29afbd914dcb1718",
    "appsecret": "d5aea93c59246e49e243e59a5f5f9ec8",
    "paykey": "36bc10cd66c88431e3b92a31586faf3f",
    "mch_id": "1518252721",
    "callback_url": "/api/order/callback"               # 下单回调地址
}

# 上传配置
UPLOAD = {
    "ext": ["jpg", "gif", "bmp", "jpeg", "png"],        # 扩展
    "prefix_path": "/web/static/upload/",               # 上传路径
    "prefix_url": "/static/upload/"                     # url地址
}

# 域名
APP = {
    "domain": "http://0.0.0.0:5000"
    # "domain": "http://test.youdian.tech"
}


# 三种支付状态
PAY_STATUS_MAPPING = {
    "1": "已支付",
    "-8": "待支付",
    "0": "已关闭"
}

# 状态值描述
PAY_STATUS_DISPLAY_MAPPING = {
    "0": "订单关闭",
    "1": "支付成功",
    "-8": "待支付",
    "-7": "待发货",
    "-6": "待确认",
    "-5": "待评价"
}