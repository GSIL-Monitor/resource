# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.schema import FetchedValue
from application import db, app


class PayOrder(db.Model):
    __tablename__ = 'pay_order'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_sn = db.Column(db.String(40), nullable=False, unique=True, server_default=db.FetchedValue())
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    total_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    yun_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    pay_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    pay_sn = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue())
    prepay_id = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue())
    note = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    express_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    express_address_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    express_info = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    comment_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    pay_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    # 返回状态值
    @property
    def pay_status(self):
        tmp_status = self.status
        if self.status == 1:
            tmp_status = self.express_status
            # 待评价(已付款，已确认，未评论)
            if self.express_status == 1 and self.comment_status == 0:
                tmp_status = -5
            # 已完成(已付款，已确认，已评论)
            if self.express_status == 1 and self.comment_status == 1:
                tmp_status = 1
        return tmp_status

    # 返回状态描述
    @property
    def status_desc(self):
        return app.config["PAY_STATUS_DISPLAY_MAPPING"][str(self.pay_status)]

    # 订单号
    @property
    def order_number(self):
        order_number = self.created_time.strftime("%Y%m%d%H%M%S")
        order_number = order_number + str(self.id).zfill(5)
        return order_number
