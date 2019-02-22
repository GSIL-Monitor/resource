# -*- coding: utf-8 -*-
"""
会员管理界面
"""
from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import i_render_template, iPagination, getCurrentDate
from common.models.member.Member import Member
from application import app, db
from common.libs.UrlManager import UrlManager

route_member = Blueprint('member_page', __name__)


@route_member.route("/index")
def index():
    resp_data = {}
    req = request.values
    query = Member.query

    # 搜索功能：混合查询
    if "mix_kw" in req:
        query = query.filter(Member.nickname.ilike("%{0}%".format(req["mix_kw"])))
    if "status" in req and int(req["status"]) > -1:
        query = query.filter(Member.status == int(req["status"]))

    # 分页
    page = int(req["p"]) if ("p" in req and req["p"]) else 1        # 如果page存在并且有值，如果没有就默认为第一页
    page_params = {
        "total": query.count(),                                     # 总共多少页
        "page_size": app.config["PAGE_SIZE"],                       # 每一页多少行数据
        "page": page,                                               # 当前页
        "display": app.config["PAGE_DISPLAY"],                      # 显示前后共多少页
        "url": request.full_path.replace("&p={}".format(page), "")  # 取出前面页更新当前页
    }
    pages = iPagination(page_params)
    offset = (page - 1) * app.config["PAGE_SIZE"]                   # 偏移量，第一页0开始，第二页50开始
    limit = app.config["PAGE_SIZE"] * page

    list = query.order_by(Member.id.desc()).all()[offset:limit]     # 通过id取出所需要的数据，倒序排列

    resp_data["list"] = list                                        # 列表数据
    resp_data["pages"] = pages                                      # 分页数据
    resp_data["search_con"] = req
    resp_data["status_mapping"] = app.config["STATUS_MAPPING"]
    resp_data["current"] = "index"
    return i_render_template("member/index.html", resp_data)


@route_member.route("/info")
def info():
    resp_data = {}
    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/member/index")
    if id < 1:
        return redirect(reback_url)
    info = Member.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)
    resp_data["info"] = info
    resp_data["current"] = "info"
    return i_render_template("member/info.html", resp_data)


# 设置用户信息
@route_member.route("/set", methods=["GET", "POST"])
def set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int(req.get("id", 0))
        reback_url = UrlManager.buildUrl("/member/index")

        if id < 1:
            return redirect(reback_url)
        info = Member.query.filter_by(id=id).first()

        if not info:
            return redirect(reback_url)

        # 用户是删除状态，不允许编辑
        if info.status != 1:
            return redirect(reback_url)

        resp_data["info"] = info
        resp_data["current"] = "index"
        return i_render_template("member/set.html", resp_data)

    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    id = req.get("id", 0)
    nickname = req.get("nickname", "")
    if nickname is None or len(nickname)<1 :
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的姓名"
        return jsonify(resp)
    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp["code"] = -1
        resp["msg"] = "指定的会员不存在"
        return jsonify(resp)

    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)


# 删除和恢复操作
@route_member.route("/ops", methods=["POST"])
def ops():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    id = req.get("id", 0)
    act = req.get("act", "")

    if not id:
        resp["code"] = -1
        resp["msg"] = "请选择要操作的账号"
        return jsonify(resp)

    if act not in ["remove", "recover"]:
        resp["code"] = -1
        resp["msg"] = "操作有误，请重试"
        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp["code"] = -1
        resp["msg"] = "指定的会员不存在"
        return jsonify(resp)

    if act == "remove":
        member_info.status = 0
    elif act == "recover":
        member_info.status = 1

    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)



@route_member.route( "/comment" )
def comment():
    return i_render_template("member/comment.html")
