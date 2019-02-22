# -*- coding: utf-8 -*-
"""
账号管理界面
"""
from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import i_render_template, iPagination, getCurrentDate
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.User import User
from common.models.log.AppAccessLog import AppAccessLog
from application import app, db
from sqlalchemy import or_

route_account = Blueprint('account_page', __name__)


# 列表展示
@route_account.route("/index")
def index():
    resp_data = {}
    query = User.query
    req = request.values

    # 搜索功能：混合查询
    if "mix_kw" in req:
        rule = or_(User.nickname.ilike("%{0}%".format(req["mix_kw"])),  # ilike忽略大小写，"%c%"表示模糊检索c
                   User.mobile.ilike("%{0}%".format(req["mix_kw"])))
        query = query.filter(rule)
    # 状态查询
    if "status" in req and int(req["status"]) > -1:
        query = query.filter(User.status == int(req["status"]))

    # 分页
    page = int(req["p"]) if ("p" in req and req["p"]) else 1            # 如果page存在并且有值，如果没有就默认为第一页
    page_params = {
        "total": query.count(),                                         # 总共多少页
        "page_size": app.config["PAGE_SIZE"],                           # 每一页多少行数据
        "page": page,                                                   # 当前页
        "display": app.config["PAGE_DISPLAY"],                          # 显示前后共多少页
        "url": request.full_path.replace("&p={}".format(page), "")      # 取出前面页更新当前页
    }
    pages = iPagination(page_params)
    offset = (page-1) * app.config["PAGE_SIZE"]                         # 偏移量，第一页0开始，第二页50开始
    limit = app.config["PAGE_SIZE"] * page

    list = query.order_by(User.uid.desc()).all()[offset:limit]          # 通过uid取出所需要的数据，倒序排列
    resp_data["list"] = list
    resp_data["pages"] = pages
    resp_data["search_con"] = req
    resp_data["status_mapping"] = app.config["STATUS_MAPPING"]
    return i_render_template("account/index.html", resp_data)


# 账户详情
@route_account.route("/info")
def info():
    resp_data = {}
    req = request.args                                                  # args只取get方式的参数
    uid = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/account/index")

    # 判断uid是否存在
    if uid < 1:
        return redirect(reback_url)

    # 判断是否存在用户信息
    info = User.query.filter_by(uid=uid).first()
    if not info:
        return redirect(reback_url)

    # 判断用户日志是否存在,通过时间倒序提取
    log = AppAccessLog.query.filter_by(uid=uid).order_by("-created_time").all()[0:5]
    if log:
        resp_data["log"] = log

    # 存在就将信息传递到前端
    resp_data["info"] = info

    return i_render_template("account/info.html", resp_data)


# 设置
@route_account.route("/set", methods=["GET", "POST"])
def set():
    # 默认密码显示
    default_pwd = "******"
    if request.method == "GET":
        resp_data = {}
        req = request.args
        uid = int(req.get("id", 0))                                         # 获取id默认值0
        user_info = None

        # 如果id存在，那么就把用户信息取出来，传入到页面
        if uid:
            user_info = User.query.filter_by(uid=uid).first()
        resp_data["user_info"] = user_info
        return i_render_template("account/set.html", resp_data)

    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values                                                    # post方法获取使用values

    id = req["id"] if "id" in req else 0
    nickname = req["nickname"] if "nickname" in req else ""
    mobile = req["mobile"] if "mobile" in req else ""
    email = req["email"] if "email" in req else ""
    login_name = req["login_name"] if "login_name" in req else ""
    login_pwd = req["login_pwd"] if "login_pwd" in req else ""

    if nickname is None or len(nickname) < 1:
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的姓名"
        return jsonify(resp)
    if mobile is None or len(mobile) < 11:
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的手机号码"
        return jsonify(resp)
    if email is None or len(email) < 1:
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的邮箱"
        return jsonify(resp)
    if login_name is None or len(login_name) < 1:
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的登录名"
        return jsonify(resp)
    if login_pwd is None or len(login_pwd) < 6:
        resp["code"] = -1
        resp["msg"] = "请输入符合规范的登录密码"
        return jsonify(resp)

    # 使用filter查询需要写类的名称，filter_by不需要
    # 查询用户名是否存在，如果新增，如果是修改
    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_in:
        resp["code"] = -1
        resp["msg"] = "该登录名已存在请换一个"
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    # 如果存在就是编辑
    if user_info:
        model_user = user_info
    # 如果不存在就是新增数据，创建时间和salt在创建时生成无需改变
    else:
        model_user = User()
        model_user.created_time = getCurrentDate()
        model_user.login_salt = UserService.geneSalt()                              # 生成一个salt值

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    # 只有用户修改密码，才进行修改，否则保持不变
    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd(login_pwd, model_user.login_salt)
    model_user.updated_time = getCurrentDate()

    db.session.add(model_user)
    db.session.commit()

    return jsonify(resp)


# 账号删除和恢复
@route_account.route("/ops", methods=["POST"])
def ops():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values                                                        # post方法获取使用values

    id = req["id"] if "id" in req else 0
    act = req["act"] if "act" in req else ""

    if not id:
        resp["code"] = -1
        resp["msg"] = "请选择需要操作的账号"
        return jsonify(resp)

    if act not in ["remove", "recover"]:
        resp["code"] = -1
        resp["msg"] = "操作有误，请重试"
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        resp["code"] = -1
        resp["msg"] = "指定账号不存在"
        return jsonify(resp)

    if act == "remove":
        user_info.status = 0
    elif act == "recover":
        user_info.status = 1

    user_info.update_time = getCurrentDate()                                      # 记得要更新时间
    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)




