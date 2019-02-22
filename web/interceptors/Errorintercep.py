"""
错误处理拦截器
"""

from application import app
from common.libs.Helper import i_render_template
from common.libs.LogService import LogService


# 捕获404错误进行处理
@app.errorhandler(404)
def error_404(e):
    LogService.addErrorLog(str(e))          # 把错误以字符串形式传入
    return i_render_template("error/error.html", {"status": 404, "msg": "很抱歉！您访问的内容不存在"})
