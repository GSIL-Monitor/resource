"""
订单展示
"""

from flask import request, jsonify, g
from web.controllers.api import route_api
from common.models.food.Food import Food
import json, decimal
from common.libs.UrlManager import UrlManager
from common.libs.pay.PayService import PayService
from common.libs.member.CartService import CartService
from common.libs.pay.WeChatService import WeChatService
from common.libs.Helper import getCurrentDate
from common.models.pay.PayOrder import PayOrder
from common.models.member.OauthMemberBind import OauthMemberBind
from application import app, db


@route_api.route("/order/info", methods=["POST"])
def orderInfo():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values
    params_goods = req["goods"] if "goods" in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dic = {}
    for item in params_goods_list:
        food_dic[item["id"]] = item["number"]                       # 购买数量

    food_ids = food_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)                   # 预留运费
    if food_list:
        for item in food_list:
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str(item.price),                           # 价格是decimal格式，json无法转义，所以要先变成字符串
                "pic_url": UrlManager.buildImageUrl(item.main_image),
                "number": food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])   # 总共需要支付的金额
            data_food_list.append(tmp_data)

    default_address = {                                             # 配送地址
        "name": "alienfist",
        "mobile": "12345678901",
        "address": "杭州市高新区"
    }

    resp["data"]["food_list"] = data_food_list
    resp["data"]["pay_price"] = str(pay_price)
    resp["data"]["yun_price"] = str(yun_price)
    resp["data"]["total_price"] = str(pay_price + yun_price)
    resp["data"]["default_address"] = default_address

    return jsonify(resp)


@route_api.route("/order/create", methods=["POST"])
def orderCreate():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values

    type = req["type"] if "type" in req else ""
    params_goods = req["goods"] if "goods" in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if len(items) < 1:
        resp["code"] = -1
        resp["msg"] = "下单失败，没有选择商品"
        return jsonify(resp)

    # 调用下单方法
    member_info = g.member_info
    target = PayService()
    params = {}
    resp = target.createOrder(member_info.id, items, params)

    # 如果来自购物车的下单成功操作，那么删除购物车
    if resp["code"] == 200 and type == "cart":
        CartService.deleteItem(member_info.id, items)

    return jsonify(resp)


@route_api.route("/order/pay", methods=["POST"])
def orderPay():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    member_info = g.member_info
    req = request.values
    order_sn = req["order_sn"] if "order_sn" in req else ""
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        resp["code"] = -1
        resp["msg"] = "系统繁忙，请稍后再试"
        return jsonify(resp)

    # 提取绑定信息获取openid
    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if not oauth_bind_info:
        resp["code"] = -1
        resp["msg"] = "系统繁忙，请稍后再试"
        return jsonify(resp)

    config_mina = app.config["MINA_APP"]
    # 拼装微信支付回调地址
    notify_url = app.config["APP"]["domain"] + config_mina["callback_url"]

    target_wechat = WeChatService(merchant_key=config_mina["paykey"])

    # 微信要求的字段
    data = {
        "appid": config_mina["appid"],                                      # 小程序的appid
        "mch_id": config_mina["mch_id"],                                    # 微信支付的商户号
        "nonce_str": target_wechat.get_nonce_str(),                         # 随机字符串（uuid生成）
        "body": "订餐",                                                    # 信息内容
        "out_trade_no": pay_order_info.order_sn,                            # 唯一的订单编号
        "total_fee": int(pay_order_info.total_price * 100),                 # 价格，单位：分
        "notify_url": notify_url,                                           # 统一回调地址
        "trade_type": "JSAPI",                                              # 公众号方式
        "openid": oauth_bind_info.openid                                    # 用户身份标识
    }

    pay_info = target_wechat.get_pay_info(data)                             # 提交订单返回信息

    # 保存prepay_id为了后面发模板消息
    pay_order_info.prepay_id = pay_info["prepay_id"]
    db.session.add(pay_order_info)
    db.session.commit()

    resp["data"]["pay_info"] = pay_info

    return jsonify(resp)


# 微信支付回调地址
@route_api.route("/order/callback", methods=["POST"])
def orderCallback():

    app.logger.info("******************回调方法******************")

    result_data = {                                                         # 返回结果
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}                            # 返回头部

    config_mina = app.config['MINA_APP']
    target_wechat = WeChatService(merchant_key=config_mina['paykey'])
    callback_data = target_wechat.xml_to_dict(request.data)

    app.logger.info(callback_data)
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    app.logger.info(gene_sign)

    # 验证回调签名和签名是否一致
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if callback_data['result_code'] != 'SUCCESS':
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 验证订单是否存在
    order_sn = callback_data['out_trade_no']
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 验证回调金额和支付金额是否相同
    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 验证状态是否为支付
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    target_pay = PayService()
    target_pay.orderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id']})

    # 需要将微信回调的结果放入记录表
    target_pay.addPayCallbackData(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header


# 取消订单 确认收货
@route_api.route("/order/ops", methods=["POST"])
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)
    elif act == "confirm":
        pay_order_info.express_status = 1
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()

    return jsonify(resp)



