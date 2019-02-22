
from werkzeug.utils import secure_filename
from application import app, db
from common.libs.Helper import getCurrentDate
import os, stat, uuid
from common.models.Images import Image


class UploadService():

    @staticmethod
    def uploadByFile(file):
        config_upload = app.config["UPLOAD"]
        resp = {"code": 200, "msg": "操作成功", "data": {}}
        filename = secure_filename(file.filename)                   # 获取一个安全的文件名
        ext = filename.rsplit(".", 1)[1]                            # 反向分割，只分割一次，取后缀名
        if ext not in config_upload["ext"]:
            resp["code"] = -1
            resp["msg"] = "不允许的扩展类型文件"
            return resp

        root_path = app.root_path + config_upload["prefix_path"]
        app.logger.info(root_path)
        file_dir = getCurrentDate("%Y%m%d")                         # 用日期来做上传文件夹名称
        save_dir = root_path + file_dir                             # 拼装出文件夹的完整路径

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)                                      # 如果文件夹不存在就新建一个
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)            # 设置文件夹的权限，777，全部权限

        # uuid可以根据硬件和时间生成一个不同字符串
        file_name = str(uuid.uuid4()).replace("-", "") + "." + ext
        file.save("{0}/{1}".format(save_dir, file_name))                 # 保存文件

        model_image = Image()
        model_image.file_key = file_dir + "/" + file_name
        model_image.created_time = getCurrentDate()
        db.session.add(model_image)
        db.session.commit()

        resp["data"] = {
            "file_key": model_image.file_key
        }

        return resp
