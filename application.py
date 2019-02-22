from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import os


class Application(Flask):
    def __init__(self, import_name, template_folder=None, root_path=None):
        super(Application, self).__init__(import_name,          # 调用Application父类初始化方法
                                          template_folder=template_folder,
                                          root_path=root_path,
                                          static_folder=None)   # 如果不需要通过这里控制静态文件路径，那么就要屏蔽掉
        self.config.from_pyfile("config/base_setting.py")       # 加载基础的配置文件
        if "ops_config" in os.environ:                          # 加载环境变量, export ops_config=local
            self.config.from_pyfile("config/%s_setting.py" % os.environ["ops_config"])

        db.init_app(self)                                       # db初始化


db = SQLAlchemy()
app = Application(__name__, template_folder=os.getcwd()+"/web/templates", root_path=os.getcwd())   # getcwd获取当前目录
manager = Manager(app)


