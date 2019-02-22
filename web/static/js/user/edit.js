;
var user_edit_ops={
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".user_edit_wrap .save").click(function () {
            //获取当前对象，设定提交状态
            var btn_target = $(this);
            if(btn_target.hasClass("disable")){
                common_ops.alert("正在处理请不要重复提交");
                return;
            }

            //获取昵称
            var nickname_target = $(".user_edit_wrap input[name=nickname]");
            var nickname = nickname_target.val();
            //获取邮箱
            var email_target = $(".user_edit_wrap input[name=email]");
            var email = email_target.val();

            //如果昵称没有或者长度小于2
            if(!nickname || nickname.length<2){
                common_ops.tip("请输入符合规范的昵称",nickname_target);
                return false;
            }
            //如果邮件没有或者长度小于2
            if(!email || email.length<2){
                common_ops.tip("请输入符合规范的邮箱",email_target);
                return false;
            }

            // 提交后就禁止按按钮
            btn_target.addClass("disable");

            var data = {
              nickname:nickname,
              email:email
            };

            $.ajax({
                url:common_ops.buildUrl("/user/edit"),
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
    user_edit_ops.init();
})