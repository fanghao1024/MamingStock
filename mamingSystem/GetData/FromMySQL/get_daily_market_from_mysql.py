'''
从MySQL数据库里读取每日数据
输入：
	code:	股票代码
	startdate:	统计起始日期，以20210412的八位字符串格式
	enddate:	统计结束日期，以20210412的八位字符串格式
返回：
	pandas.DataFrame格式
	date：	交易日期
	code：	股票代码
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

def get_daily_market_information(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from daily_market where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			return df
		else:
			return None

def get_daily_market_qfq(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from daily_market where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			return df.loc[:,['date','code','qfq_open','qfq_high','qfq_low','qfq_close','volume','outstanding_share','turnover']]
		else:
			return None

def get_daily_market_qfq_from_dfcf(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from dailyline where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df.rename(columns={'qfq_open': 'open', 'qfq_high': 'high', 'qfq_low': 'low', 'qfq_close': 'close'},
					  inplace=True)
			df = df.sort_values(by='date', ascending=True)
			df = df[
				['date', 'code', 'open', 'high', 'low', 'close', 'volume', 'deal', 'zhenfu', 'zhangdiefu',
				 'zhangdiee', 'turnover']]
			return df
		else:
			return None

def get_daily_market_bfq(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from daily_market where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			return df.loc[:,['date','code','bfq_open','bfq_high','bfq_low','bfq_close','volume','outstanding_share','turnover']]
		else:
			return None

def get_daily_market_bfq_from_dfcf(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from dailyline where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index) != 0:
			df.rename(columns={'bfq_open':'open','bfq_high':'high','bfq_low':'low','bfq_close':'close'},inplace=True)
			df = df.sort_values(by='date', ascending=True)
			df=df[['date', 'code', 'open', 'high', 'low', 'close', 'volume','deal','zhenfu','zhangdiefu','zhangdiee', 'turnover']]
			return df
		else:
			return None

def get_daily_market_hfq(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from daily_market where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			return df.loc[:,['date','code','hfq_open','hfq_high','hfq_low','hfq_close','volume','outstanding_share','turnover']]
		else:
			return None

def get_daily_market_hfq_from_dfcf(code='000001',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where code="+code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where code="+code
	#sql="select * from daily_market"
	sql='select * from dailyline where code="{0}" and date >="{1}" and date<="{2}"'.format(code,startdate,enddate)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			return df.loc[:,['date','code','hfq_open','hfq_high','hfq_low','hfq_close','volume','deal','zhenfu','zhangdiefu','zhangdiee', 'turnover']]
		else:
			return None

#a=get_daily_market_information('600095','20200101','20211231')
#a=get_daily_market_bfq_from_dfcf('000001')
#print(a)