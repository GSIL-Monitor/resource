"""
小程序会员入口
需要在初始化文件中引入
"""

from web.controllers.api import route_api
from flask import request, jsonify, g
from application import db
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.food.WxShareHistory import WxShareHistory
from common.libs.Helper import getCurrentDate
from common.libs.member.MemberService import MemberService


# 微信小程序用户注册
@route_api.route("/member/login", methods=["POST", "GET"])
def login():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    code = req["code"] if "code" in req else ""
    if not code or len(code) < 1:
        resp["code"] = -1
        resp["msg"] = "需要code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenid(code)
    if openid is None:
        resp["code"] = -1
        resp["msg"] = "调用微信出错"
        return jsonify(resp)

    # 判断是否已经注册
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()

    # 如果没有就进入注册流程
    if not bind_info:
        model_member = Member()
        model_member.nickname = req.get("nickName", "")
        model_member.sex = req.get("gender", 0)
        model_member.avatar = req.get("avatarUrl", "")
        model_member.salt = MemberService.geneSalt()
        model_member.updated_time = model_member.created_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        # 建立绑定关系
        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id      # 先前提交已经产生了这个id
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ""
        model_bind.updated_time = model_bind.created_time = getCurrentDate()
        db.session.add(model_bind)
        db.session.commit()

        bind_info = model_bind

    member_info = Member.query.filter_by(id=bind_info.member_id).first()

    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp["data"] = {"token": token}
    return jsonify(resp)


# 判断是否登录，登录的话就不用发起微信获取用户信息的请求了
@route_api.route("/member/check-reg", methods=["GET", "POST"])
def checkReg():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    code = req.get("code", "")
    if not code or len(code) < 1:
        resp["code"] = -1
        resp["msg"] = "需要code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenid(code)
    if openid is None:
        resp["code"] = -1
        resp["msg"] = "调用微信出错"
        return jsonify(resp)

    # 判断是否已经注册
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        resp["code"] = -1
        resp["msg"] = "未绑定"
        return jsonify(resp)

    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    if not member_info:
        resp["code"] = -1
        resp["msg"] = "未查询到绑定信息"
        return jsonify(resp)

    token = "%s#%s"%(MemberService.geneAuthCode(member_info), member_info.id)
    resp["data"] = {"token": token}

    return jsonify(resp)


# 记录小程序分享
@route_api.route("/member/share", methods=["POST"])
def memberShare():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    url = req["url"] if "url" in req else ""
    member_info = g.member_info                             # 来自于拦截器的信息

    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add(model_share)
    db.session.commit()

    return jsonify(resp)


# 展示用户信息
@route_api.route("/member/info")
def memberInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    resp['data']['info'] = {
        "nickname": member_info.nickname,
        "avatar_url": member_info.avatar
    }
    return jsonify(resp)
