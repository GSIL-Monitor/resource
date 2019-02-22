import base64
import hashlib
import string
import random


class UserService():

    # 对用户密码进行加密
    @staticmethod
    def genePwd(pwd, salt):
        md5 = hashlib.md5()
        newstr = "%s-%s" % (base64.encodebytes(pwd.encode("utf-8")), salt)      # python3都是unicode需要先转码成byte
        md5.update(newstr.encode("utf-8"))
        return md5.hexdigest()                                                  # 返回摘要，作为十六进制数据字符串值

    # 产生授权码
    @staticmethod
    def geneAuthCode(user_info):
        md5 = hashlib.md5()
        newstr = "%s-%s-%s-%s" % (user_info.uid, user_info.login_name, user_info.login_pwd, user_info.login_salt)
        md5.update(newstr.encode("utf-8"))
        return md5.hexdigest()

    # 产生salt
    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice(string.ascii_letters+string.digits) for i in range(length)]
        return "".join(keylist)
