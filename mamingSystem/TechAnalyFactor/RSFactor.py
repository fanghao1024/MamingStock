import sys,os
import pandas as pd
os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')

import get_daily_index_market_from_mysql
import get_daily_industry_market_from_mysql
import get_daily_market_from_mysql
import get_daily_ETF_market_from_mysql

func_dist={'stock':get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf,\
    'index':get_daily_index_market_from_mysql.get_daily_index_market_information,\
        'board':get_daily_industry_market_from_mysql.get_daily_board_market_bfq_from_dfcf,\
            'ETF':get_daily_ETF_market_from_mysql.get_ETF_daily_market_information}

def fun_none():
    print('wrong type')
    return None

def RSFactor(codeA,typeA,codeB,typeB,startday,endday):
    print(codeA,typeA,codeB,typeB,startday,endday)
    A=func_dist.get(typeA,fun_none)(codeA,startday,endday)
    B=func_dist.get(typeB,fun_none)(codeB,startday,endday)
    A.rename(columns={'open':'A_open','high':'A_high','low':'A_low','close':'A_close'},inplace=True)
    B.rename(columns={'open': 'B_open', 'high': 'B_high', 'low': 'B_low', 'close': 'B_close'}, inplace=True)

    A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'trade_date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    print(A)

    B['trade_date'] = B['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    B.rename(columns={'trade_date': 'datetime'}, inplace=True)
    B['datetime'] = pd.to_datetime(B['datetime'])
    B.set_index(['datetime'], inplace=True)
    print(B)

    A=pd.merge(A,B,left_index=True,right_index=True)
    A['RS']=A['A_close']/A['B_close']
    return A[['RS']]

#print(RSFactor('000001','stock','399006','index','20210101','20220101'))