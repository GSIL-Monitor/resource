"""
本地开发需要该文件
解决无法加载静态文件的问题
"""

from flask import Blueprint, send_from_directory
from application import app


route_static = Blueprint("static", __name__)


@route_static.route("/<path:filename>")
def index(filename):
    return send_from_directory(app.root_path + "/web/static/", filename)      # 根目录+加上静态文件路径
