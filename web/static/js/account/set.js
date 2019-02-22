;
var account_set_ops={
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".wrap_account_set .save").click(function () {
            //获取当前对象，设定提交状态
            var btn_target = $(this);
            if(btn_target.hasClass("disable")){
                common_ops.alert("正在处理请不要重复提交");
                return;
            }

            //获取昵称
            var nickname_target = $(".wrap_account_set input[name=nickname]");
            var nickname = nickname_target.val();
            //获取手机
            var mobile_target = $(".wrap_account_set input[name=mobile]");
            var mobile = mobile_target.val();
            //获取邮箱
            var email_target = $(".wrap_account_set input[name=email]");
            var email = email_target.val();
            //获取用户名
            var login_name_target = $(".wrap_account_set input[name=login_name]");
            var login_name = login_name_target.val();
            //获取密码
            var login_pwd_target = $(".wrap_account_set input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();


            //如果昵称没有或者长度小于2
            if(!nickname || nickname.length<2){
                common_ops.tip("请输入符合规范的昵称",nickname_target);
                return false;
            }
            //如果手机没有或者长度小于11
            if(!mobile || mobile.length<11){
                common_ops.tip("请输入符合规范的手机",mobile_target);
                return false;
            }
            //如果邮件没有或者长度小于2
            if(!email || email.length<2){
                common_ops.tip("请输入符合规范的邮箱",email_target);
                return false;
            }
            //如果用户名没有或者长度小于2
            if(!login_name || login_name.length<2){
                common_ops.tip("请输入符合规范的用户名",login_name_target);
                return false;
            }
            //如果密码没有或者长度小于6
            if(!login_pwd || login_pwd.length<6){
                common_ops.tip("请输入符合规范的登录密码",login_pwd_target);
                return false;
            }

            // 提交后就禁止按按钮
            btn_target.addClass("disable");

            var data = {
                nickname:nickname,
                mobile:mobile,
                email:email,
                login_name:login_name,
                login_pwd:login_pwd,
                id:$(".wrap_account_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl("/account/set"),
                type:"POST",
                data:data,
                dataType:"json",
                success:function (res) {
                    //获取完成后改回初始状态
                    btn_target.removeClass("disable");
                    var callback = null;
                    if(res.code == 200){
                        callback = function () {
                            //完成后跳转到用户首页
                            window.location.href = common_ops.buildUrl("/account/index")
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            })
        })
    }
};

$(document).ready(function () {
    account_set_ops.init();
})