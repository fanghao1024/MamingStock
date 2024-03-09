import pandas as pd
import datetime
import pymysql
import os
import requests
import logging
import traceback
from sqlalchemy import create_engine

logger = logging.getLogger()

def stock_sse_summary() -> pd.DataFrame:
    """
    上海证券交易所-总貌
    http://www.sse.com.cn/market/stockdata/statistic/
    :return: 上海证券交易所-总貌
    :rtype: pandas.DataFrame
    """
    url = "http://www.sse.com.cn/market/stockdata/statistic/"
    r = requests.get(url)
    r.encoding = "utf-8"
    big_df = pd.DataFrame()
    temp_list = ["总貌", "主板", "科创板"]
    for i in range(len(pd.read_html(r.text))):
        for j in range(0, 2):
            inner_df = pd.read_html(r.text)[i].iloc[:, j].str.split("  ", expand=True)
            inner_df["item"] = temp_list[i]
            big_df = big_df.append(inner_df)
    big_df.dropna(how="any", inplace=True)
    big_df.columns = ["item", "number", "type"]
    big_df = big_df[["type", "item", "number"]]
    return big_df

def get_sh_daily_summary_mysql():
    engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')

    #获取当日上证的概览数据
    ss_daily_summay=stock_sse_summary()
    #往数据添加一列日期
    date=datetime.date.today().strftime('%Y%m%d')
    table_name=str(date)
    date_list=[table_name]*ss_daily_summay.shape[0]
    ss_daily_summay.insert(0,'date',date_list)

    try:
        ss_daily_summay.to_sql(name='sh_summary_data',con=engine,index=False, if_exists = 'append')
    except Exception as ee:
        logger.error('get_sh_daily_summary_mysql fileToMysql fialed',ee)
        traceback.print_exc()
    finally:
        engine.dispose()


