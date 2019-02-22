
import decimal
from application import app, db
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackData
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
import hashlib, time, decimal, random
from common.libs.Helper import getCurrentDate
from common.libs.food.FoodService import FoodService
from common.libs.queue.QueueService import QueueService


class PayService():
    def __init__(self):
        pass

    # 创建订单
    def createOrder(self, member_id, items=None, params=None):
        resp = {"code": 200, "msg": "操作成功", "data": {}}
        pay_price = decimal.Decimal(0.00)

        continue_cnt = 0                                    # 跳过次数
        foods_id = []
        for item in items:
            if decimal.Decimal(item["price"]) < 0:          # 如果价格小于0就跳过
                continue_cnt += 1
                continue
            pay_price = pay_price + decimal.Decimal(item["price"]) * int(item["number"])
            foods_id.append(item["id"])

        if continue_cnt >= len(items):                     # 如果跳过次数和商品总数相同，那么说明为空
            resp["code"] = -1
            resp["msg"] = "商品items为空"
            return resp

        yun_price = params["yun_price"] if params and "yun_price" in params else 0          # 运费
        note = params["note"] if params and "note" in params else ""                        # 备注

        yun_price = decimal.Decimal(yun_price)
        total_price = pay_price + yun_price             # 总价

        # 并发处理，一个人在操作数据库，其他人不能同时操作

        try:
            # 这一步比较关键，通过with_for_update锁死的这几条数据查询
            tmp_food_list = db.session.query(Food).filter(Food.id.in_(foods_id)).with_for_update().all()

            tmp_food_stock_mapping = {}
            for tmp_item in tmp_food_list:
                tmp_food_stock_mapping[tmp_item.id] = tmp_item.stock            # 库存总量

            # 主表的操作
            model_pay_order = PayOrder()
            model_pay_order.order_sn = self.geneOrderSn()
            model_pay_order.member_id = member_id
            model_pay_order.total_price = total_price
            model_pay_order.yun_price = yun_price
            model_pay_order.pay_price = pay_price
            model_pay_order.note = note
            model_pay_order.status = -8                         # 待支付状态
            model_pay_order.express_status = -8                 # 待支付过程
            model_pay_order.updated_time = model_pay_order.created_time = getCurrentDate()
            db.session.add(model_pay_order)

            for item in items:
                tmp_left_stock = tmp_food_stock_mapping[item["id"]]         # 剩余库存
                if decimal.Decimal(item["price"]) < 0:                      # 单价小于0跳过
                    continue
                if int(item["number"]) > int(tmp_left_stock):               # 超过库存报错
                    raise Exception("您购买的美食太火爆，剩余：%s，您购买：%s" % (tmp_left_stock, item["number"]))

                # 修改库存操作
                tmp_ret = Food.query.filter_by(id=item["id"]).update({
                    "stock": int(tmp_left_stock) - int(item["number"])
                })
                if not tmp_ret:
                    raise Exception("下单失败请重新下单")

                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = model_pay_order.id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item["number"]
                tmp_pay_item.price = item["price"]
                tmp_pay_item.food_id = item["id"]
                tmp_pay_item.note = note
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentDate()
                db.session.add(tmp_pay_item)

                # 库存变更日志,操作数量是减少库存就是负
                FoodService.setStockChangeLog(item["id"], -item["number"], "在线购买")

            db.session.commit()

            # 成功提交后返回给前端数据
            resp["data"] = {
                "id": model_pay_order.id,
                "order_sn": model_pay_order.order_sn,
                "total_price": str(total_price)
            }

        except Exception as e:
            # 报错后数据要回滚
            db.session.rollback()
            print(e)
            resp["code"] = -1
            resp["msg"] = "下单失败，请重新下单"
            resp["msg"] = str(e)
            return resp

        return resp

    # 取消订单
    def closeOrder(self, pay_order_id=0):
        if pay_order_id < 1:
            return False
        pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
        if pay_order_items:
            # 需要归还库存
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if tmp_food_info:
                    tmp_food_info.stock = tmp_food_info.stock + item.quantity
                    tmp_food_info.updated_time = getCurrentDate()
                    db.session.add(tmp_food_info)
                    db.session.commit()
                    # 变更库存日志
                    FoodService.setStockChangeLog(item.food_id, item.quantity, "订单取消")

        pay_order_info.status = 0                                   # 状态变更为0
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return True

    # 订单支付成功后执行的回调函数
    def orderSuccess(self, pay_order_id=0, params=None):
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
            # 如果数据查询不到，或者状态码不是-8，-7，返回成功
            if not pay_order_info or pay_order_info.status not in [-8, -7]:
                return True

            # 第三方流水号
            pay_order_info.pay_sn = params["pay_sn"] if params and "pay_sn" in params else ""
            pay_order_info.status = 1                           # 修改为已支付状态码
            pay_order_info.express_status = -7                  # 快递修改为待发送状态
            pay_order_info.pay_time = getCurrentDate()          # 支付时间
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)

            # 售卖历史,写入数据库
            pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
            for order_item in pay_order_items:
                tmp_model_sale_log = FoodSaleChangeLog()
                tmp_model_sale_log.food_id = order_item.food_id
                tmp_model_sale_log.quantity = order_item.quantity
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentDate()
                db.session.add(tmp_model_sale_log)

            db.session.commit()

        # 报错后数据回滚
        except Exception as e:
            db.session.rollback()
            return False

        # 队列消息
        QueueService.addQueue("pay", {
            "member_id": pay_order_info.member_id,
            "pay_order_id": pay_order_info.id
        })

    # 微信支付返回数据写入
    def addPayCallbackData(self, pay_order_id=0, type="pay", data=""):
        model_callback = PayOrderCallbackData()
        model_callback.pay_order_id = pay_order_id
        if type == "pay":                               # 发生支付
            model_callback.pay_data = data
            model_callback.refund_data = ""
        else:                                           # 发生退款
            model_callback.refund_data = data
            model_callback.pay_data = ""
        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    # 随机订单号的生成
    def geneOrderSn(self):
        m = hashlib.md5()
        sn = None

        # 要查询数据库确定是否唯一
        while True:
            # 字符串由时间戳和随机数构成
            str = "%s-%s" % (int(round(time.time()*1000)), random.randint(0, 9999999))
            m.update(str.encode("utf-8"))
            sn = m.hexdigest()
            # 如果查询不到，就可以跳出循环
            if not PayOrder.query.filter_by(order_sn=sn).first():
                break
        return sn


