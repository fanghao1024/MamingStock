import akshare as ak
import pandas as pd
import logging
import traceback
import pymysql
import time
from sqlalchemy import create_engine
#pd.set_option('display.max_columns', 500)

'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE daily_market'
cur.execute(sql)
db.commit()
db.close()
'''


def get_daily_market_price_from_dfcf(startday, endday):
	engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
	stock_info_a_code_name_df = ak.stock_info_a_code_name()

	mark = False
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):

		print(code, name)

		#if mark == False and str(code) != '000153':
		#	continue
		#else:
		#	mark = True
		#time.sleep(1)
		#if str(code) == '689009' or str(code) == '688616':
		#	continue
		# 前复权数据
		while True:
			try:
				stock_zh_a_daily_qfq_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=startday,
														end_date=endday, adjust="")

				stock_zh_a_daily_qfq_df.insert(1, 'code', code)
				stock_zh_a_daily_qfq_df.columns = ['date', 'code', 'bfq_open', 'bfq_close', 'bfq_high', 'bfq_low',
												   'volume','deal', 'zhenfu','zhangdiefu','zhangdiee', 'turnover']
				stock_daily_market = stock_zh_a_daily_qfq_df.copy()
				stock_daily_market['date']=pd.to_datetime(stock_daily_market['date'],format='%Y-%m-%d')
				stock_daily_market['date'] = stock_daily_market['date'].apply(lambda x:x.strftime('%Y%m%d'))
				# 前复权数据
				stock_zh_a_daily_bfq_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=startday,
														end_date=endday, adjust="qfq")
				stock_daily_market['qfq_open'] = stock_zh_a_daily_bfq_df['开盘']
				stock_daily_market['qfq_close'] = stock_zh_a_daily_bfq_df['收盘']
				stock_daily_market['qfq_high'] = stock_zh_a_daily_bfq_df['最高']
				stock_daily_market['qfq_low'] = stock_zh_a_daily_bfq_df['最低']


				# 后复权数据
				stock_zh_a_daily_hfq_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=startday,
														end_date=endday, adjust="hfq")

				stock_daily_market['hfq_open'] = stock_zh_a_daily_hfq_df['开盘']
				stock_daily_market['hfq_close'] = stock_zh_a_daily_hfq_df['收盘']
				stock_daily_market['hfq_high'] = stock_zh_a_daily_hfq_df['最高']
				stock_daily_market['hfq_low'] = stock_zh_a_daily_hfq_df['最低']
				break
			except:
				print('connect wrong')
				time.sleep(5)
				continue


		order = ['date', 'code', 'qfq_open', 'qfq_high', 'qfq_low', 'qfq_close', 'bfq_open', 'bfq_high',
				 'bfq_low', 'bfq_close', 'hfq_open', 'hfq_high', 'hfq_low', 'hfq_close', 'volume', 'deal', 'zhenfu','zhangdiefu','zhangdiee', 'turnover']
		stock_daily_market = stock_daily_market[order]

		try:
			print(stock_daily_market)
			stock_daily_market.to_sql(name='dailyline', con=engine, index=False, if_exists='append')
		except Exception as ee:
			logger = logging.getLogger()
			logger.error('get_sz_period_summary fileToMysql fialed', ee)
			traceback.print_exc()
	engine.dispose()


get_daily_market_price_from_dfcf('20220228', '20220228')
