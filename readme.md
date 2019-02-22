Python Flask订餐系统

# 启动
* export ops_config=local|production
* python manager.py runserver


# 根据数据库表生成model
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables user --outfile "common/models/User.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables app_access_log --outfile "common/models/log/AppAccessLog.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables app_error_log --outfile "common/models/log/AppErrorLog.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables member --outfile "common/models/member/Member.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables oauth_member_bind --outfile "common/models/member/OauthMemberBind.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables food --outfile "common/models/food/Food.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables food_cat --outfile "common/models/food/FoodCat.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables food_sale_change_log --outfile "common/models/food/FoodSaleChangeLog.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables food_stock_change_log --outfile "common/models/food/FoodStockChangeLog.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables images --outfile "common/models/food/Images.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables wx_share_history --outfile "common/models/food/WxShareHistory.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables member_cart --outfile "common/models/member/MemberCart.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables member_address --outfile "common/models/member/MemberAddress.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables member_comments --outfile "common/models/member/MemberComments.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables pay_order --outfile "common/models/pay/PayOrder.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables pay_order_callback_data --outfile "common/models/pay/PayOrderCallbackData.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables pay_order_item --outfile "common/models/pay/PayOrderItem.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables queue_list --outfile "common/models/queue/QueueList.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables oauth_access_token --outfile "common/models/pay/OauthAccessToken.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables stat_daily_food --outfile "common/models/stat/StatDailyFood.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables stat_daily_member --outfile "common/models/stat/StatDailyMember.py"  --flask
flask-sqlacodegen 'mysql+pymysql://root:bj237237@127.0.0.1/food_db' --tables stat_daily_site --outfile "common/models/stat/StatDailySite.py"  --flask