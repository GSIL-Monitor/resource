;
var food_cat_set_ops={
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".wrap_cat_set .save").click(function () {
            //获取当前对象，设定提交状态
            var btn_target = $(this);
            if(btn_target.hasClass("disable")){
                common_ops.alert("正在处理请不要重复提交");
                return;
            }

            //获取菜品分类名称
            var name_target = $(".wrap_cat_set input[name=name]");
            var name = name_target.val();
            //获取菜品分类权重
            var weight_target = $(".wrap_cat_set input[name=weight]");
            var weight = weight_target.val();

            //如果分类名称长度小于1
            if(name.length<1){
                common_ops.tip("请输入符合规范的分类名称", name_target);
                return false;
            }
            //如果权重小于1
            if(parseInt(weight)<1){
                common_ops.tip("请输入符合规范的权重,并且至少大于1", weight_target);
                return false;
            }

            // 提交后就禁止按按钮
            btn_target.addClass("disable");

            var data = {
                name:name,
                weight:weight,
                id:$(".wrap_cat_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl("/food/cat-set"),
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
                            window.location.href = common_ops.buildUrl("/food/cat")
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            })
        })
    }
};

$(document).ready(function () {
    food_cat_set_ops.init();
})