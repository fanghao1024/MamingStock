import tushare as ts
import pandas as pd
import os
import datetime

ts.set_token('2c9828c59d60c4564ecdfb7ce0726d0f44b16cfcb8c1d4a4bd503165')

des_path='data/priceData'

pro = ts.pro_api()
trade_date = pro.trade_cal(exchange='', start_date='20080828', end_date='20210316')
trade_date=trade_date[trade_date.is_open==1]
trade_dates=list(trade_date['cal_date'])
print(type(trade_dates))
print(trade_dates)
for date in trade_dates:
	filename=date+'.xlsx'
	filename=os.path.join(des_path,filename)
	dateBaseData=pro.daily(trade_date=date)
	dateBaseData.to_excel(filename)
'''
history_data = pro.daily(trade_date=trade_dates)
df=pd.DataFrame(history_data)
fileName=str(datetime.datetime.now())
fileName=fileName.replace('-','').replace(' ','').replace(':','')[:14]
fileName=fileName+'.xlsx'
df.to_excel(os.path.join(des_path,fileName))
'''