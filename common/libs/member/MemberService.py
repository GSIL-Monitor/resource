
import hashlib
import string
import random
import requests
import json
from application import app


class MemberService():

    # 产生授权码
    @staticmethod
    def geneAuthCode(member_info = None):
        md5 = hashlib.md5()
        newstr = "%s-%s-%s" % (member_info.id, member_info.salt, member_info.status)
        md5.update(newstr.encode("utf-8"))
        return md5.hexdigest()

    # 产生salt
    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice(string.ascii_letters+string.digits) for i in range(length)]
        return "".join(keylist)

    # 获取openid
    @staticmethod
    def getWeChatOpenid(code):
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format(
            app.config["MINA_APP"]["appid"], app.config["MINA_APP"]["appsecret"], code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = None
        if "openid" in res:
            openid = res["openid"]
        return openid
