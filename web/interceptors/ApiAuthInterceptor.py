"""
API拦截器
每一次请求都会验证是否登录
会员拦截器
"""

from application import app
from flask import request, g, jsonify
from common.models.member.Member import Member
from common.libs.member.MemberService import MemberService
import re


# api认证
@app.before_request
def before_request():
    api_ignore_urls = app.config["API_IGNORE_URLS"]
    path = request.path

    # 如果不是api页面不做拦截
    if "/api" not in path:
        return

    member_info = check_member_login()
    g.member_info = None
    if member_info:
        g.member_info = member_info                 # 存入member_info可以给分享页面使用

    # 不拦截url
    pattern = re.compile("%s" % "|".join(api_ignore_urls))
    if pattern.match(path):
        return

    if not member_info:
        resp = {"code": -1, "msg": "未登录", "data": {}}
        return jsonify(resp)

    return


# 判断会员是否登录
def check_member_login():
    # 读取cookies
    auth_cookie = request.headers.get("Authorization")

    # 判断是否存在cookie
    if auth_cookie is None:
        return False

    # 分割cookie（abcdef#uid）,判断长度是否为2
    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False

    try:
        # 通过id从数据库提取用户信息
        member_info = Member.query.filter_by(id=auth_info[1]).first()
        if member_info is None:
            return False
    except Exception:
        return False

    # 如果生成的cookies部分密码不符合返回false
    if auth_info[0] != MemberService.geneAuthCode(member_info):
        return False

    # 用户被删除状态发生改变退出登录
    if member_info.status != 1:
        return False

    return member_info
