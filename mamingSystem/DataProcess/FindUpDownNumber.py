import sys
import logging
import traceback
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import akshare as ak
import getStockInfoByDate
from sqlalchemy import create_engine
import pandas as pd


#pd.set_option('display.max_columns', None)
# The above could be sent to an independent module

from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def getUpDownNumber(startday='00000000',endday='99999999'):
    stock_tradedays = pd.read_excel('../data/tradeDays.xlsx')

    for row in stock_tradedays['trade_date']:
        if str(row)<startday or str(row)>endday:
            continue
        a=getStockInfoByDate.get_stock_info_by_date(row)
        up=0
        down=0
        flat=0
        up_exchange=0
        down_exchange=0
        a['bfq_close']=a['bfq_close'].astype(float)
        a['bfq_open']=a['bfq_open'].astype(float)
        a['change']=a['bfq_close']-a['bfq_open']
        print(a)
        b=a['change']>0.001
        up_exchange=a[['volume']][a['change']>0.001].sum()
        up=b.sum()
        b=a['change']<-0.001
        down=b.sum()
        flat=len(a)-up-down
        down_exchange = a[['volume']][a['change'] < -0.001].sum()
        print(up,'===',up_exchange,'---',down,'----',down_exchange,'====',flat)

def getAllUpDownNumber_from_dfcf(startday='00000000',endday='99999999'):
    stock_tradedays = pd.read_excel('../data/tradeDays.xlsx')
    engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
    for row in stock_tradedays['trade_date']:

        if str(row)<startday or str(row)>endday:
            continue

        a=getStockInfoByDate.get_stock_info_by_date_from_dfcf(row)

        i=0
        UpAndDown = pd.DataFrame(columns=['trade_date','name','up','down','flat','up_amount','down_amount','flat_amount'])
        # 采用.loc的方法进行

        a['bfq_close']=a['bfq_close'].astype(float)
        a['bfq_open']=a['bfq_open'].astype(float)
        a['change']=a['bfq_close']-a['bfq_open']
        print(a)

        #北上深
        b = a['change'] >= 0.001
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = a['change'] <= -0.001
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001)
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'All', up, down, flat, up_exchange, down_exchange, flat_exchange]


        #除去北交所的全A
        i=i+1
        b=(a['change']>=0.001) & ((a['code'].str.startswith('6')) | (a['code'].str.startswith('3')) | (a['code'].str.startswith('0')))
        up_exchange=a[['deal']][b].apply(lambda x:x.sum()).values[0]
        up=b.sum()
        c=(a['change']<=-0.001) & ((a['code'].str.startswith('6')) | (a['code'].str.startswith('3'))| (a['code'].str.startswith('0')))
        down=c.sum()
        down_exchange = a[['deal']][c].apply(lambda x:x.sum()).values[0]
        d = (a['change'] > -0.001) & ( a['change'] < 0.001 ) & ((a['code'].str.startswith('6')) | (a['code'].str.startswith('3')) | (a['code'].str.startswith('0')))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row),'AllA',up,down,flat,up_exchange,down_exchange,flat_exchange]


        #上证
        i = i + 1
        b = (a['change'] >= 0.001)& (a['code'].str.startswith('6'))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change']<=-0.001) & (a['code'].str.startswith('6'))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001)& (a['code'].str.startswith('6'))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'SH', up, down, flat, up_exchange, down_exchange, flat_exchange]

        #上证主板
        i = i + 1
        b = (a['change'] >= 0.001) & (a['code'].str.startswith('60'))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change'] <= -0.001) & (a['code'].str.startswith('60'))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001) & (a['code'].str.startswith('60'))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'SHZB', up, down, flat, up_exchange, down_exchange, flat_exchange]
        # 科创板
        i = i + 1
        b = (a['change'] >= 0.001) & (a['code'].str.startswith('688'))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change'] <= -0.001) & (a['code'].str.startswith('688'))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001) & (a['code'].str.startswith('688'))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'KCB', up, down, flat, up_exchange, down_exchange, flat_exchange]

        #深证主板
        i = i + 1
        b = (a['change'] >= 0.001) & (a['code'].str.startswith('0'))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change'] <= -0.001) & (a['code'].str.startswith('0'))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001) & (a['code'].str.startswith('0'))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'SZZB', up, down, flat, up_exchange, down_exchange, flat_exchange]

        #创业板
        i = i + 1
        b = (a['change'] >= 0.001) & (a['code'].str.startswith('3'))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change'] <= -0.001) & (a['code'].str.startswith('3'))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001) & (a['code'].str.startswith('3'))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'CYB', up, down, flat, up_exchange, down_exchange, flat_exchange]

        #深证
        i = i + 1
        UpAndDown.loc[i]=UpAndDown.loc[i-1]+UpAndDown.loc[i-2]
        UpAndDown.loc[i,'trade_date']=str(row)
        UpAndDown.loc[i,'name']='SZ'

        #北交所
        i = i + 1
        b = (a['change'] >= 0.001) & ((a['code'].str.startswith('8')) | (a['code'].str.startswith('4')))
        up_exchange = a[['deal']][b].apply(lambda x: x.sum()).values[0]
        up = b.sum()
        c = (a['change'] <= -0.001) & ((a['code'].str.startswith('8')) | (a['code'].str.startswith('4')))
        down = c.sum()
        down_exchange = a[['deal']][c].apply(lambda x: x.sum()).values[0]
        d = (a['change'] > -0.001) & (a['change'] < 0.001) & ((a['code'].str.startswith('8')) | (a['code'].str.startswith('4')))
        flat = d.sum()
        flat_exchange = a[['deal']][d].apply(lambda x: x.sum()).values[0]
        UpAndDown.loc[i] = [str(row), 'BJ', up, down, flat, up_exchange, down_exchange, flat_exchange]




        try:
            print(UpAndDown)
            UpAndDown.to_sql(name='upanddown', con=engine, index=False, if_exists='append')
        except Exception as ee:
            logger = logging.getLogger()
            logger.error('get_sz_period_summary fileToMysql fialed', ee)
            traceback.print_exc()
    engine.dispose()
#'20090101'-'20220214' 20080101-20081021
getAllUpDownNumber_from_dfcf('20220218','20220228')