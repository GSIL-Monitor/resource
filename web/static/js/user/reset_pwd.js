;
var mod_pwd_ops={
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $("#save").click(function () {
            //获取当前对象，设定提交状态
            var btn_target = $(this);
            if(btn_target.hasClass("disable")){
                common_ops.alert("正在处理请不要重复提交");
                return;
            }

            //获取密码
            var old_password = $("#old_password").val();
            var new_password = $("#new_password").val();

            //如果昵称没有或者长度小于2
            if(!old_password){
                common_ops.alert("请输入原密码");
                return false;
            }
            //如果邮件没有或者长度小于2
            if(!new_password || new_password.length<6){
                common_ops.alert("请输入不少于6位新密码");
                return false;
            }

            // 提交后就禁止按按钮
            btn_target.addClass("disable");

            var data = {
              old_password:old_password,
              new_password:new_password
            };

            $.ajax({
                url:common_ops.buildUrl("/user/reset-pwd"),
                type:"POST",
                data:data,
                dataType:"json",
                success:function (res) {
                    //获取完成后改回初始状态
                    btn_target.removeClass("disable");
                    var callback = null;
                    if(res.code == 200){
                        callback = function () {
                            //刷新当前页面
                            window.location.href = window.location.href
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            })
        })
    }
};

$(document).ready(function () {
    mod_pwd_ops.init();
})