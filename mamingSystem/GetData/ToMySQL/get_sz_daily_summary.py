# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2021/2/10 14:31
Desc: 市场总貌
http://www.szse.cn/market/overview/index.html
http://www.sse.com.cn/market/stockdata/statistic/
"""
from io import BytesIO

import requests
import tushare as ts
import pandas as pd
import datetime
import pymysql
import os
import requests
import logging
import traceback
from sqlalchemy import create_engine

logger = logging.getLogger()
engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')

ts.set_token('2c9828c59d60c4564ecdfb7ce0726d0f44b16cfcb8c1d4a4bd503165')


pro = ts.pro_api()

def stock_szse_summary(date: str = "20200619") -> pd.DataFrame:
    """
    深证证券交易所-总貌
    http://www.szse.cn/market/overview/index.html
    :param date: 最近结束交易日
    :type date: str
    :return: 深证证券交易所-总貌
    :rtype: pandas.DataFrame
    """
    url = "http://www.szse.cn/api/report/ShowReport"
    params = {
        "SHOWTYPE": "xlsx",
        "CATALOGID": "1803_sczm",
        "TABKEY": "tab1",
        "txtQueryDate": "-".join([date[:4], date[4:6], date[6:]]),
        "random": "0.39339437497296137",
    }
    r = requests.get(url, params=params)
    temp_df = pd.read_excel(BytesIO(r.content), engine="xlrd")
    temp_df["证券类别"] = temp_df["证券类别"].str.strip()
    temp_df.iloc[:, 2:] = temp_df.iloc[:, 2:].applymap(lambda x: x.replace(",", ""))
    return temp_df

def get_sz_period_summary(startday,endday):
	#trade_date = pro.trade_cal(exchange='', start_date='20140917', end_date='20210317')
	trade_date = pro.trade_cal(exchange='', start_date=startday, end_date=endday)
	trade_date = trade_date[trade_date.is_open == 1]
	trade_dates = list(trade_date['cal_date'])
	for date in trade_dates:
		dateBaseData=stock_szse_summary(date=date)
		date_list = [date] * dateBaseData.shape[0]
		dateBaseData.insert(0, '交易日期', date_list)
		#print(dateBaseData)
		try:
			dateBaseData.to_sql(name='sz_summary_data', con=engine, index=False, if_exists='append')
		except Exception as ee:
			logger.error('get_sz_period_summary fileToMysql fialed', ee)
			traceback.print_exc()
	engine.dispose()


