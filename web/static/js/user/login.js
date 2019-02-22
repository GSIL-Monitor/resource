//分号是防止代码被压缩时候出错
;

var user_login_ops = {
    //外部调用的方法
    init:function () {
        this.eventBind();
    },
    //事件绑定
    eventBind:function () {
        //获取当前对象，设定提交状态
        var btn_target = $(this);
        if(btn_target.hasClass("disable")){
            common_ops.alert("正在处理请不要重复提交");
            return;
        }

        //点击事件方法
        $(".login_wrap .do-login").click(function () {
            var login_name = $(".login_wrap input[name=login_name]").val();
            var login_pwd = $(".login_wrap input[name=login_pwd]").val();
            //判断参数都是合法
            if (login_name==undefined || login_name.length<1){
                common_ops.alert("请输入正确的登录用户名");
                return;
            }
            if (login_pwd==undefined || login_pwd.length<1){
                common_ops.alert("请输入正确的登录用户名");
                return;
            }

            //点击提交后修改当前状态
            btn_target.addClass("disable");

            //ajax提交
            $.ajax({
                url:common_ops.buildUrl("/user/login"),
                type:"POST",
                data:{"login_name":login_name, "login_pwd":login_pwd},
                dataType:"json",
                success:function (res) {
                    //获取完成后改回初始状态
                    btn_target.removeClass("disable");
                    var callback = null;
                    if(res.code == 200){
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/")
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            })
        })
    }
};

//页面加载完成时候执行
$(document).ready(function () {
    user_login_ops.init();
});

