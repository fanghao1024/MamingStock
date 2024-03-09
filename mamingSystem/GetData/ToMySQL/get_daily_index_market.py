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


def get_index_market_price_from_dfcf(startday, endday):
	engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
	stock_info_a_code_name_df = pd.read_excel('../../data/index_code.xlsx',converters={u'code':str})

	mark = False
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code, name)

		#if mark == False and str(code) != '000971':
		#	continue
		#else:
		#	mark = True

		#if str(code) == '689009' or str(code) == '688616':
		#	continue

		if str(code).startswith('0'):
			stock_code = 'sh' + str(code)
		else:
			stock_code = 'sz' + str(code)

		while True:
			try:
				index_daily_market = ak.stock_zh_index_daily_em(symbol=stock_code)
				break
			except:
				print('connect wrong')
				time.sleep(5)
				continue

		index_daily_market.insert(1, 'code', code)
		index_daily_market.insert(2, 'name', name)
		index_daily_market.columns = ['date', 'code', 'name','open','close','high','low','volume','amount']

		index_daily_market['date']=pd.to_datetime(index_daily_market['date'],format='%Y-%m-%d')
		index_daily_market['date'] = index_daily_market['date'].apply(lambda x:x.strftime('%Y%m%d'))
		index_daily=index_daily_market[(index_daily_market['date']>=startday) & (index_daily_market['date']<=endday)]

		try:
			print(index_daily)
			index_daily.to_sql(name='indexline', con=engine, index=False, if_exists='append')
		except Exception as ee:
			logger = logging.getLogger()
			logger.error('get_sz_period_summary fileToMysql fialed', ee)
			traceback.print_exc()
	engine.dispose()


get_index_market_price_from_dfcf('20220228', '20220228')
