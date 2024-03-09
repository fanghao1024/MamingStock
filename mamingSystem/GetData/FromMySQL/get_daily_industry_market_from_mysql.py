import pymysql
from sqlalchemy import create_engine
import pandas as pd
pymysql.install_as_MySQLdb()

def get_daily_industry_market_information(ETF_code='BK0726',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where stock_code="+stock_code
	#sql="select * from daily_market"
	sql='select * from industryline where code="{0}"'.format(ETF_code)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df.sort_values(by='date', ascending=True)
			df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]
			return df
		else:
			return None

def get_daily_board_market_bfq_from_dfcf(ETF_code='BK0726',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
	#sql="select * from daily_market where stock_code="+stock_code
	#sql="select * from daily_market"
	sql='select * from industryline where code="{0}"'.format(ETF_code)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index) != 0:
			df = df.sort_values(by='date', ascending=True)
			df = df[(df['date'] >= startdate) & (df['date'] <= enddate)]
			df.rename(columns={'bfq_open':'open','bfq_high':'high','bfq_low':'low','bfq_close':'close'},inplace=True)
			df=df[['date', 'code', 'open', 'high', 'low', 'close', 'volume','amount','zhenfu','turnover']]
			return df
		else:
			return None

#print(get_daily_industry_market_information())