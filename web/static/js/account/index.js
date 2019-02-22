;
var account_index_ops = {
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        var that = this
        $(".wrap_search .search").click(function () {
            // 表单提交
            $(".wrap_search").submit();
        });
        $(".remove").click(function () {
            //通过attr获取属性
            that.ops("remove", $(this).attr("data"))
        });
        $(".recover").click(function () {
            that.ops("recover", $(this).attr("data"))
        })
    },
    //删除和恢复函数
    ops:function (act,id) {
        var callback = {
            "ok":function () {
                $.ajax({
                    url:common_ops.buildUrl("/account/ops"),
                    type:"POST",
                    data:{
                        act:act,
                        id:id
                    },
                    dataType:"json",
                    success:function (res) {
                        var callback = null;
                        if(res.code == 200){
                            callback = function(){
                                //刷新当前页面
                                window.location.href = window.location.href
                            }
                        }
                        common_ops.alert(res.msg,callback);
                    }
                })
            },
            "cancel":null
        };
        common_ops.confirm((act=="remove" ? "确定删除？":"确定恢复？"), callback)

    }
};

$(document).ready(function () {
    account_index_ops.init();
})