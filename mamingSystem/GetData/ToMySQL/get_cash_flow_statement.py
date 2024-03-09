import akshare as ak
import akshare as ak
import logging
import traceback
import pymysql
import time
from sqlalchemy import create_engine
import pandas as pd
pd.set_option('display.max_columns', None)
'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE the_cash_flow_statement'
cur.execute(sql)
db.commit()
db.close()
'''


def get_cash_flow_statement(day):
	stock_info_a_code_name_df = ak.stock_info_a_code_name()
	engine_the_cash_flow_statement = create_engine('mysql+pymysql://root:@localhost:3308/stockdata')
	mark = False
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code,name)
		#if (mark == False and str(code) != '300321') :
		#	continue
		#else:
		#	mark = True
		time.sleep(2)
		stock_financial_report_sina_df = ak.stock_financial_report_sina(stock=code, symbol='现金流量表')
		if len(stock_financial_report_sina_df.columns) < 3:
			print(code, name, 'have no the cash-flow statement')
			continue
		stock_financial_report_sina_df = stock_financial_report_sina_df[
			stock_financial_report_sina_df['报表日期'] > day]
		if stock_financial_report_sina_df.shape[0] < 1:
			continue
		stock_financial_report_sina_df.insert(0, 'stock_code', code)

		print(stock_financial_report_sina_df)
		try:
			stock_financial_report_sina_df.to_sql(name='the_cash_flow_statement', con=engine_the_cash_flow_statement,
												  index=False, if_exists='append')
		except Exception as ee:
			logger = logging.getLogger()
			logger.error('get_the_cash_flow_sheet fileToMysql fialed', ee)

			traceback.print_exc()
			filename = day + '_cash_flow_statement.csv'

			df_loss = pd.DataFrame([day, code, name, 'Exception']).T
			print(df_loss)
			df_loss.to_csv(filename, mode='a')

	engine_the_cash_flow_statement.dispose()

get_cash_flow_statement('00000000')