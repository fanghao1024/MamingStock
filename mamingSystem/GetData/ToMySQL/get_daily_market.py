import akshare as ak
import pandas as pd
import logging
import traceback
import pymysql
from sqlalchemy import create_engine


'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE daily_market'
cur.execute(sql)
db.commit()
db.close()
'''




def get_daily_market_price(startday,endday):

    engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    mark=False
    for code,name in zip(stock_info_a_code_name_df['code'],stock_info_a_code_name_df['name']):
        print(code,name)

        #if mark == False and str(code) != '300563':
        #    continue
        #else:
        #    mark = True

        if str(code)=='689009' or str(code)=='688616':
            continue
        if str(code).startswith('0') or str(code).startswith('3'):
            code='sz'+str(code)
        else:
            code='sh'+str(code)
        #前复权数据
        print(code,name)
        stock_daily_market=pd.DataFrame()
        stock_zh_a_daily_qfq_df = ak.stock_zh_a_daily(symbol=code, start_date=startday, end_date=endday, adjust="qfq")
        #stock_zh_a_daily_qfq_df.insert(0, 'date', stock_zh_a_daily_qfq_df.index)
        stock_zh_a_daily_qfq_df.insert(1, 'code', code)

        #print(stock_zh_a_daily_qfq_df)
        stock_zh_a_daily_qfq_df.columns=['date', 'code', 'qfq_open', 'qfq_high', 'qfq_low', 'qfq_close', 'volume','outstanding_share', 'turnover']
        stock_daily_market=stock_zh_a_daily_qfq_df.copy()
        stock_daily_market['date']=stock_daily_market['date'].dt.strftime('%Y%m%d')


        #不复权数据
        stock_zh_a_daily_bfq_df= ak.stock_zh_a_daily(symbol=code, start_date=startday, end_date=endday)
        stock_zh_a_daily_bfq_df.insert(0, 'date', stock_zh_a_daily_bfq_df.index)
        stock_zh_a_daily_bfq_df.insert(1, 'code', code)
        stock_daily_market['bfq_open']=stock_zh_a_daily_bfq_df['open']
        stock_daily_market['bfq_high'] = stock_zh_a_daily_bfq_df['high']
        stock_daily_market['bfq_low'] = stock_zh_a_daily_bfq_df['low']
        stock_daily_market['bfq_close'] = stock_zh_a_daily_bfq_df['close']

        #后复权数据
        stock_zh_a_daily_hfq_df= ak.stock_zh_a_daily(symbol=code, start_date=startday, end_date=endday, adjust="hfq")
        stock_zh_a_daily_hfq_df.insert(0, 'date', stock_zh_a_daily_qfq_df.index)
        stock_zh_a_daily_hfq_df.insert(1, 'code', code)
        stock_daily_market['hfq_open'] = stock_zh_a_daily_hfq_df['open']
        stock_daily_market['hfq_high'] = stock_zh_a_daily_hfq_df['high']
        stock_daily_market['hfq_low'] = stock_zh_a_daily_hfq_df['low']
        stock_daily_market['hfq_close'] = stock_zh_a_daily_hfq_df['close']

        order=['date', 'code', 'qfq_open', 'qfq_high', 'qfq_low','qfq_close','bfq_open','bfq_high','bfq_low','bfq_close','hfq_open','hfq_high','hfq_low','hfq_close', 'volume', 'outstanding_share', 'turnover']
        stock_daily_market=stock_daily_market[order]
    

        try:
            print(stock_daily_market)
            stock_daily_market.to_sql(name='daily_market', con=engine, index=False, if_exists='append')
        except Exception as ee:
            logger = logging.getLogger()
            logger.error('get_sz_period_summary fileToMysql fialed', ee)
            traceback.print_exc()
    engine.dispose()



get_daily_market_price('20220129','20220211')
