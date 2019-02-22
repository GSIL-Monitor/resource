"""
上传功能
"""

from flask import Blueprint, request, jsonify
from application import app, db
import json, re
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Images import Image

route_upload = Blueprint("upload_page",__name__)


@route_upload.route("/ueditor", methods=["POST", "GET"])    # 上传图片是post,获取配置文件是get
def ueditor():
    req = request.values
    action = req.get("action", "")

    if action == "config":
        root_path = app.root_path
        config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format(root_path)
        with open (config_path) as fp:
            try:
                config_data = json.loads(re.sub(r'/\*.*\*/', '', fp.read()))   # re.sub()正则替换
            except:
                config_data = {}
        return jsonify(config_data)

    # 图片上传动作
    if action == "uploadimage":
        return uploadImage()

    # 图片展示动作
    if action == "listimage":
        return listImage()

    return "upload"

# 无刷新上传封面图
@route_upload.route("/pic", methods=["GET", "POST"])
def uploadPic():
    file_target = request.files                         # 获取请求文件表单
    upfile = file_target.get("pic", None)               # 获取上传的file
    callback_target = "window.parent.upload"            # 当前窗口子调用父的方法
    if upfile is None:                                  # 如果不存在就返回一个js事件
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败")
    ret = UploadService.uploadByFile(upfile)            # 上传图片事件
    if ret["code"] != 200:                              # 如果上传失败，返回一个js事件
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败" + ret["msg"])

    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target, ret["data"]["file_key"])


# 图片上传函数
def uploadImage():
    resp = {"state": "SUCCESS", "url": "", "title": "", "original": ""}
    file_target = request.files
    upfile = file_target.get("upfile", None)    # 文件类型
    if upfile is None:
        resp["state"] = "上传失败"
        return jsonify(resp)

    ret = UploadService.uploadByFile(upfile)

    if ret["code"] != 200:
        resp["state"] = "上传失败" + ret["msg"]
        return jsonify(resp)

    resp["url"] = UrlManager.buildImageUrl(ret["data"]["file_key"])

    return jsonify(resp)


# 图片展示函数
def listImage():
    resp = {"state": "SUCCESS", "list": [], "start": 0, "total": 0}
    req = request.values
    start = int(req.get("start", 0))
    page_size = int(req.get("size", 20))

    # 分页的实现，通过id方式，可以加快搜索速度
    query = Image.query
    if start > 0:
        query = query.filter(Image.id < start)

    list = query.order_by(Image.id.desc()).limit(page_size).all()    # 分页取回数据倒序展示

    images = []
    if list:
        for item in list:
            images.append({"url": UrlManager.buildImageUrl(item.file_key)})
            start = item.id
    resp["start"] = start
    resp["list"] = images
    resp["total"] = len(images)
    return jsonify(resp)
