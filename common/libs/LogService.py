"""
日志对象
"""

from flask import request, g
from common.models.log.AppAccessLog import AppAccessLog
from common.models.log.AppErrorLog import AppErrorLog
from common.libs.Helper import getCurrentDate
from application import app, db
import json


class LogService():
    # 添加浏览记录
    @staticmethod
    def addAccessLog():
        target = AppAccessLog()                     # 实例化数据模型
        target.target_url = request.url
        target.referer_url = request.referrer
        target.ip = request.remote_addr
        target.query_params = json.dumps(request.values.to_dict())

        if "current_user" in g and g.current_user is not None:
            target.uid = g.current_user.uid

        target.ua = request.headers.get("User-Agent")
        target.created_time = getCurrentDate()
        db.session.add(target)
        db.session.commit()
        return True

    # 添加错误记录
    @staticmethod
    def addErrorLog(content):
        target = AppErrorLog()                      # 实例化数据模型
        target.target_url = request.url
        target.referer_url = request.referrer
        target.query_params = json.dumps(request.values.to_dict())
        target.content = content
        target.created_time = getCurrentDate()
        db.session.add(target)
        db.session.commit()
        return True
