import pymysql
from sqlalchemy import create_engine
import pandas as pd
pymysql.install_as_MySQLdb()

def get_daily_upanddown_information(name='AllA',startdate='19901217',enddate='21000101'):
	db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
						 charset='utf8')
	# 定义要执行的SQL语句
	#sql = "select * from daily_market where stock_code="+stock_code+'and trade_date>='+startdate+' and trade_date<='+enddate
	#sql="select * from daily_market where stock_code="+stock_code
	#sql="select * from daily_market"
	sql='select * from upanddown where name="{0}"'.format(name)
	try:

		df = pd.read_sql(sql, con=db)

	except Exception as e:
		raise e
	finally:
		db.close()  # 关闭连接
		if len(df.index)!=0:
			df = df[(df['trade_date'] >= startdate)&(df['trade_date'] <= enddate)]
			df=df.sort_values(by='trade_date', ascending=True)
			return df
		else:
			return None

#print(get_daily_upanddown_information())