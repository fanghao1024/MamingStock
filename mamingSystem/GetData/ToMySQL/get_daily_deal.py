import akshare as ak
import tushare as ts
import logging
import traceback
import pymysql
from sqlalchemy import create_engine

ts.set_token('2c9828c59d60c4564ecdfb7ce0726d0f44b16cfcb8c1d4a4bd503165')

'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE deal_record'
cur.execute(sql)
db.commit()
db.close()
'''

def get_daily_deal_information(startday,endday):
	engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
	stock_info_a_code_name_df = ak.stock_info_a_code_name()
	mark=False
	pro = ts.pro_api()
	tradeDay=pro.trade_cal(exchange='', start_date=startday, end_date=endday)

	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code,name)
		#if (mark == False and str(code) != '603063'):
		if (mark == False and str(code) != '300564'):
			continue
		else:
			mark = True
		if str(code).startswith('0') or str(code).startswith('3'):
			stock_code = 'sz' + str(code)
		else:
			stock_code = 'sh' + str(code)
		print('hello')
		trade_date = tradeDay.copy()
		trade_date = trade_date[trade_date.is_open == 1]
		trade_dates = list(trade_date['cal_date'])
		trade_dates.reverse()
		k=0
		for date in trade_dates:
			print('date:',date)
			print('stock_code:',stock_code)
			stock_zh_a_tick_tx_df = ak.stock_zh_a_tick_tx(code=stock_code, trade_date=date)

			if(len(stock_zh_a_tick_tx_df.columns)!=6):
				k+=1
				if k>10:
					break
				else:
					continue


			date_list = [date] * stock_zh_a_tick_tx_df.shape[0]
			code_list=[str(code)]*stock_zh_a_tick_tx_df.shape[0]
			stock_zh_a_tick_tx_df.insert(0, 'trade_date', date_list)
			stock_zh_a_tick_tx_df.insert(1, 'stock_code', code_list)
			print(stock_zh_a_tick_tx_df)
			try:
				stock_zh_a_tick_tx_df.to_sql(name='deal_record', con=engine, index=False, if_exists='append')
			except Exception as ee:
				logger = logging.getLogger()
				logger.error('get_sz_period_summary fileToMysql fialed', ee)
				traceback.print_exc()
	engine.dispose()

#get_daily_deal_information('19901219','20210317')
get_daily_deal_information('20210426','20210507')