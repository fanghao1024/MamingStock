import akshare as ak
import logging
import traceback
import pymysql
from sqlalchemy import create_engine
import time
import pandas as pd
pd.set_option('display.max_columns', None)
'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE the_balance_sheet'
cur.execute(sql)
db.commit()
db.close()
'''

def get_financial_report(day):
	stock_info_a_code_name_df = ak.stock_info_a_code_name()
	engine_the_Balance_Sheet = create_engine('mysql+pymysql://root:@localhost:3308/stockdata')
	mark = False
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code,name)
		if (mark == False and str(code) != '300639') :
			continue
		else:
			mark = True
		time.sleep(2)
		stock_financial_report_sina_df = ak.stock_financial_report_sina(stock=code, symbol='资产负债表')
		if len(stock_financial_report_sina_df.columns) < 3:
			print(code, name, 'have no the balance sheet')
			continue
		stock_financial_report_sina_df = stock_financial_report_sina_df[
			stock_financial_report_sina_df['报表日期'] > day]
		if stock_financial_report_sina_df.shape[0] < 1:
			continue
		stock_financial_report_sina_df.insert(0, 'stock_code', code)

		print(stock_financial_report_sina_df)
		try:
			stock_financial_report_sina_df.to_sql(name='the_balance_sheet', con=engine_the_Balance_Sheet,
												  index=False, if_exists='append')
		except Exception as ee:
			logger = logging.getLogger()
			logger.error('get_the_balance_sheet fileToMysql fialed', ee)

			traceback.print_exc()
			filename = day + '.csv'

			df_loss = pd.DataFrame([day, code, name, 'Exception']).T
			print(df_loss)
			df_loss.to_csv(filename, mode='a')

	engine_the_Balance_Sheet.dispose()

get_financial_report('00000000')