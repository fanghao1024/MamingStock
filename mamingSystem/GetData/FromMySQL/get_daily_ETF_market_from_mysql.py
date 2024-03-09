'''
从MySQL数据库里读取每日数据
输入：
	stock_code:	股票代码
	startdate:	统计起始日期，以20210412的八位字符串格式
	enddate:	统计结束日期，以20210412的八位字符串格式
返回：
	pandas.DataFrame格式
	date：	交易日期
	stock_code：	股票代码
	qfq_open：		前复权开盘价
	qfq_high：		前复权最高价
	qfq_low：		前复权最低价
	qfq_close：		前复权收盘价
	bfq_open：		不复权开盘价
	bfq_high：		不复权最高价
	bfq_low：		不复权最低价
	bfq_close：		不复权收盘价
	hfq_open：		后复权开盘价
	hfq_high：		后复权最高价
	hfq_low：		后复权最低价
	hfq_close：		后复权收盘价
	volume：		成交量(股)
	outstanding_share：流动股本(股)
	turnover：		换手率=成交量(股)/流动股本(股)
'''
import pymysql
from sqlalchemy import create_engine
import pandas as pd
pymysql.install_as_MySQLdb()

def get_ETF_daily_market_information(code='sz159999',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where stock_code="+stock_code
	#sql="select * from daily_market"
	sql='select * from ETF_market where code="{0}"'.format(code)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]
			return df
		else:
			return None


#print(get_ETF_daily_market_information())