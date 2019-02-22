from application import app, manager
from flask_script import Server
import traceback
import sys
import www
from jobs.launcher import runJob


# 自定义命令
manager.add_command("runserver", Server(host="0.0.0.0",
                    port=app.config["SERVER_PORT"], use_debugger=True, use_reloader=True))


# job entrance
manager.add_command("runjob", runJob())


def main():
    manager.run()               # 通过自定义命令启动


if __name__ == '__main__':
    try:
        sys.exit(main())        # exit会抛出一个异常SystemExit，如果异常没被捕获，解释器退出。如果捕获该异常，那么代码还是会执行。
    except Exception as e:
        traceback.print_exc()   # 异常打印
