"""
微信支付方法的封装
"""
import hashlib, requests, uuid, json, datetime
import xml.etree.ElementTree as ET
from application import app, db
from common.models.pay.OauthAccessToken import OauthAccessToken
from common.libs.Helper import getCurrentDate


class WeChatService():
    def __init__(self, merchant_key=None):
        self.merchant_key = merchant_key    # 微信商户支付秘钥

    # 生成微信要求的支付签名字符串
    def create_sign(self, pay_data):
        # ascii排序然后整理字符串
        stringA = "&".join(["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
        # 拼装支付秘钥
        stringSignTemp = "{0}&key={1}".format(stringA, self.merchant_key)
        # 字符串md5加密
        sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()
        # 返回结果为全部大写的字符串
        return sign.upper()

    # 获取支付信息
    def get_pay_info(self, pay_data=None):
        sign = self.create_sign(pay_data)
        pay_data["sign"] = sign
        xml_data = self.dict_to_xml(pay_data)
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        headers = {
            "Content-Type": "application/xml"
        }
        r = requests.post(url=url, data=xml_data.encode("utf-8"), headers=headers)
        r.encoding = "utf-8"

        app.logger.info(r.text)                 # 打印看一下是否返回正常的xml

        if r.status_code == 200:                # 如果请求返回200正常
            prepay_id = self.xml_to_dict(r.text).get("prepay_id")
            pay_sign_data = {
                "appId": pay_data.get("appid"),
                "timeStamp": pay_data.get("out_trade_no"),      # 时间戳
                "nonceStr": pay_data.get("nonce_str"),          # 随机字符串
                "package": "prepay_id={0}".format(prepay_id),
                "signType": "MD5"
            }
            pay_sign = self.create_sign(pay_sign_data)          # 生成统一签名，签名需要appId，所以一开始要添加
            pay_sign_data.pop("appId")                          # 签名生成之后，不需要appId，所以要删除
            pay_sign_data["paySign"] = pay_sign                 # 签名
            pay_sign_data["prepay_id"] = prepay_id
            return pay_sign_data

        return False

    # 字典转xml
    def dict_to_xml(self, dict_data):
        xml = ["<xml>"]
        for k, v in dict_data.items():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    # xml转dict
    def xml_to_dict(self, xml_data):
        xml_dict = {}
        root = ET.fromstring(xml_data)          # 获取根节点
        for child in root:
            xml_dict[child.tag] = child.text
        return xml_dict

    # 生成微信支付要求的随机字符串，只要32位都可以
    def get_nonce_str(self):
        return str(uuid.uuid4()).replace("-", "")

    # 队列发送微信模板消息需要ACCESS_TOKEN参数
    def getAccessToken(self):
        token = None

        # 查询一下过期时间是否大于当前时间，如果大于说明还没过期，直接读取token不用去请求
        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time >= getCurrentDate()).first()
        if token_info:
            token = token_info.access_token
            return token

        config_mina = app.config["MINA_APP"]
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}" \
            .format(config_mina['appid'], config_mina['appkey'])

        # 通过appid和appkey向微信发起请求获取token,有效期两个小时，存入数据表
        r = requests.get(url=url)
        if r.status_code != 200 or not r.text:
            return token

        data = json.loads(r.text)                                               # 返回信息是json格式

        now = datetime.datetime.now()                                           # 获取当前时间
        date = now + datetime.timedelta(seconds=data['expires_in'] - 200)       # 计算过期时间，预留一点空间扣去200秒

        model_token = OauthAccessToken()
        model_token.access_token = data['access_token']
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")
        model_token.created_time = getCurrentDate()
        db.session.add(model_token)
        db.session.commit()

        return data['access_token']



