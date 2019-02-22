"""
路由管理器
"""
import time
from application import app


class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl(path):
        return path

    # 版本管理
    @staticmethod
    def buildStaticUrl(path):
        release_version = app.config.get("RELEASE_VERSION")
        # 如果设置了版本号，那么就取默认版本号，如果没有定义比如开发环境，那么就随时变化
        ver = "%s" % (int(time.time())) if not release_version else release_version   # 版本号随时间变化，可以保证js实时刷新
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    # 图片地址
    @staticmethod
    def buildImageUrl(path):
        app_config = app.config["APP"]
        url = app_config["domain"] + app.config["UPLOAD"]["prefix_url"] + path
        return url


'''
函数模板, 将方法注入到模板中使用
'''
app.add_template_global(UrlManager.buildStaticUrl, "buildStaticUrl")
app.add_template_global(UrlManager.buildUrl, "buildUrl")
app.add_template_global(UrlManager.buildImageUrl, "buildImageUrl")