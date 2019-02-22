"""
拦截器
每一次请求都会验证是否登录
"""

from application import app
from flask import request, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
from common.libs.LogService import LogService
import re


# 登录验证
@app.before_request
def before_request():
    ignore_urls = app.config["IGNORE_URLS"]
    ignore_check_login_urls = app.config["IGNORE_CHECK_LOGIN_URLS"]
    path = request.path

    # 如果正则匹配为静态页面，直接返回，不用验证
    pattern_static = re.compile("%s" % "|".join(ignore_check_login_urls))
    if pattern_static.match(path):
        return

    # api页面不用认证
    if "/api" in path:
        return

    # 如果正则匹配为登录页面，直接返回，不用验证
    pattern_login = re.compile("%s" % "|".join(ignore_urls))
    if pattern_login.match(path):
        return

    # 如果验证不通过，就返回到登录页面
    user_info = check_login()
    if not user_info:
        return redirect(UrlManager.buildUrl("/user/login"))
    else:
        # 如果用户登录，保存在g变量
        g.current_user = user_info

    # 加入用户日志
    LogService.addAccessLog()

    return


# 判断用户是否已经登录
def check_login():
    cookies = request.cookies
    # 读取cookies
    auth_cookie = cookies[app.config["AUTH_COOKIE_NAME"]] if app.config["AUTH_COOKIE_NAME"] in cookies else None

    # 判断是否存在cookie
    if auth_cookie is None:
        return False

    # 分割cookie（abcdef#uid）,判断长度是否为2
    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False

    try:
        # 通过uid从数据库提取用户信息
        user_info = User.query.filter_by(uid=auth_info[1]).first()
        if user_info is None:
            return False
    except Exception:
        return False

    # 如果生成的cookies部分密码不符合返回false
    if auth_info[0] != UserService.geneAuthCode(user_info):
        return False

    # 用户被删除状态发生改变退出登录
    if user_info.status != 1:
        return False

    return user_info
