import akshare as ak
import pandas as pd
import logging
import traceback
import pymysql
from sqlalchemy import create_engine
#pd.set_option('display.max_columns', 500)
import time
'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE daily_market'
cur.execute(sql)
db.commit()
db.close()
'''


def get_hangye_market_price_from_dfcf(startday, endday):
	engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
	stock_info_a_code_name_df = pd.read_excel('../../data/hangye_dfcf.xlsx',converters={u'code':str})

	mark = False
	for stock_code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(stock_code, name)

		#if mark == False and str(stock_code) != 'BK0454':
		#	continue
		#else:
		#	mark = True

		#if str(code) == '689009' or str(code) == '688616':
		#	continue

		while True:
			try:
				bankuai_daily_market =ak.stock_board_industry_hist_em(symbol=name, adjust="")

				bankuai_daily_market.insert(1, 'code', stock_code)
				bankuai_daily_market.insert(2, 'name', name)
				bankuai_daily_market.columns = ['date', 'code', 'name','bfq_open','bfq_close','bfq_high','bfq_low','zhangdiefu','zhangdiee','volume','amount','zhenfu','turnover']

				bankuai_daily_market['date']=pd.to_datetime(bankuai_daily_market['date'],format='%Y-%m-%d')
				bankuai_daily_market['date'] = bankuai_daily_market['date'].apply(lambda x:x.strftime('%Y%m%d'))

				bankuai_zh_a_daily_bfq_df = ak.stock_board_industry_hist_em(symbol=name, adjust="qfq")
				bankuai_daily_market['qfq_open'] = bankuai_zh_a_daily_bfq_df['开盘']
				bankuai_daily_market['qfq_close'] = bankuai_zh_a_daily_bfq_df['收盘']
				bankuai_daily_market['qfq_high'] = bankuai_zh_a_daily_bfq_df['最高']
				bankuai_daily_market['qfq_low'] = bankuai_zh_a_daily_bfq_df['最低']

				# 后复权数据
				stock_zh_a_daily_hfq_df = ak.stock_board_industry_hist_em(symbol=name, adjust="hfq")

				bankuai_daily_market['hfq_open'] = stock_zh_a_daily_hfq_df['开盘']
				bankuai_daily_market['hfq_close'] = stock_zh_a_daily_hfq_df['收盘']
				bankuai_daily_market['hfq_high'] = stock_zh_a_daily_hfq_df['最高']
				bankuai_daily_market['hfq_low'] = stock_zh_a_daily_hfq_df['最低']
				break
			except:
				print('connect wrong')
				time.sleep(5)
				continue

		order = ['date', 'code','name', 'qfq_open', 'qfq_high', 'qfq_low', 'qfq_close', 'bfq_open', 'bfq_high',
				 'bfq_low', 'bfq_close', 'hfq_open', 'hfq_high', 'hfq_low', 'hfq_close', 'zhangdiefu','zhangdiee','volume','amount','zhenfu','turnover']

		bankuai_daily = bankuai_daily_market[
			(bankuai_daily_market['date'] >= startday) & (bankuai_daily_market['date'] <= endday)]
		bankuai_daily = bankuai_daily[order]
		try:
			print(bankuai_daily)
			bankuai_daily.to_sql(name='industryline', con=engine, index=False, if_exists='append')
		except Exception as ee:
			logger = logging.getLogger()
			logger.error('get_sz_period_summary fileToMysql fialed', ee)
			traceback.print_exc()
	engine.dispose()


get_hangye_market_price_from_dfcf('20220228', '20220228')
