import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import pandas as pd
import numpy as np
#pd.set_option('display.max_columns', None)
import datetime
from datetime import timedelta
from pylab import mpl
import akshare as ak

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

zero=1e-4
delta_month=12

a=ak.stock_board_industry_name_em()
print(a)

'''
allStock=pd.DataFrame()
tradeSeries['trade_date']=tradeSeries['trade_date'].astype(str)
allStock=tradeSeries[(tradeSeries['trade_date']>=startday) & (tradeSeries['trade_date']<=endday)][['trade_date']].copy()
allStock.set_index(['trade_date'], inplace=True)
print(allStock)
for index,row in stock_catalog.iterrows():
	stock_code=row[0]
	stock_name=row[1]
	print(stock_code,stock_name)
	stock_close = get_daily_market_from_mysql.get_daily_market_qfq(stock_code, startday, endday)
	if stock_close is None:
		continue
	stock_close=stock_close[['trade_date','qfq_close']]
	stock_close['trade_date']=stock_close['trade_date'].astype(str)
	stock_close.set_index(['trade_date'],inplace=True)
	stock_close.rename(columns={'qfq_close':stock_code},inplace=True)
	allStock = pd.merge(allStock, stock_close, left_on='trade_date', right_on='trade_date', how='left')

allStock.to_excel('allstock.xlsx')
print(allStock)
'''