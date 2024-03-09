import akshare as ak
import pandas as pd
from sqlalchemy import create_engine
import logging
import traceback
import re
import time


'''
for code in ETF.iloc[:,0]:
    print(code)
    fund_em_etf_fund_info_df = ak.fund_em_etf_fund_info(fund=code)
    print(fund_em_etf_fund_info_df)
'''
#fund_em_etf_fund_info_df = ak.fund_em_etf_fund_info(fund="511280")
#print(fund_em_etf_fund_info_df)

def get_daily_ETF_price_by_code(code,startday,endday):
    '''
                净值日期      单位净值    累计净值   日增长率  申购状态  赎回状态
    0     2021-10-15  124.8030  1.2610  -0.04  场内买入  场内卖出
    1     2021-10-14  124.8550  1.2610  -0.01  场内买入  场内卖出
    2     2021-10-13  124.8710  1.2620  -0.01  场内买入  场内卖出
    3     2021-10-12  124.8780  1.2620  -0.03  场内买入  场内卖出
    4     2021-10-11  124.9150  1.2620  -0.18  场内买入  场内卖出
    '''
    #fund_em_etf_fund_info_df = ak.fund_em_etf_fund_info(fund=code)
    fund_em_etf_fund_info_df=ak.fund_etf_hist_sina(symbol=code)
    #fund_em_etf_fund_info_df=fund_em_etf_fund_info_df[::-1]

    fund_em_etf_fund_info_df['date']=fund_em_etf_fund_info_df['date'].astype(str)
    fund_em_etf_fund_info_df['date']=fund_em_etf_fund_info_df['date'].apply(lambda x:re.sub('-','',x))
    fund_em_etf_fund_info_df=fund_em_etf_fund_info_df[(fund_em_etf_fund_info_df['date']>=startday)&(fund_em_etf_fund_info_df['date']<=endday)]
    #fund_em_etf_fund_info_df.reset_index(inplace=True)
    #fund_em_etf_fund_info_df.drop('index', axis=1, inplace=True)

    return fund_em_etf_fund_info_df

def get_daily_ETF_price(startday='00000000',endday='21000101'):
    engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
    #ETFs = pd.read_excel('../../data/name.xlsx')
    ETF_category=ak.fund_etf_category_sina(symbol="ETF基金")
    mark=False
    for code,name in zip(ETF_category.iloc[:, 0],ETF_category.iloc[:,1]):
        print(code,name)
        #if mark==False and code!='sh501000':
        #    continue
        #elif mark==False and code=='sh501000':
        #    mark=True
        #    continue
        while True:
            try:
                fund_em_etf_fund_info_df = get_daily_ETF_price_by_code(code,startday,endday)
                break
            except:
                print('connect wrong')
                time.sleep(5)
                continue

        fund_em_etf_fund_info_df.insert(1, 'code', code)
        fund_em_etf_fund_info_df.insert(2, 'name', name)
        #fund_em_etf_fund_info_df.rename(columns={'date':'trade_date'},inplace=True)
        # 净值日期  code         name      单位净值    累计净值   日增长率  申购状态  赎回状态

        try:
            print(fund_em_etf_fund_info_df)
            fund_em_etf_fund_info_df.to_sql(name='ETF_market', con=engine, index=False, if_exists='append')
        except Exception as ee:
            logger = logging.getLogger()
            logger.error('ETF_market fileToMysql fialed', ee)
            traceback.print_exc()
    engine.dispose()

get_daily_ETF_price('20220228','20220228')