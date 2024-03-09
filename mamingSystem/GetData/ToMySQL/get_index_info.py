import akshare as ak
import logging
import traceback
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import re

'''
db=pymysql.connect(host='localhost',port=3308,user='root',passwd='88888888',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE index_info'
cur.execute(sql)
db.commit()
db.close()
'''

def get_all_index_code_and_name():
    index_catalog=pd.read_excel('../../data/指数名单.xlsx')
    return index_catalog

def get_index_info_by_code(index_code='sh000300',startday='19901219',endday='21000101'):
    index_info = ak.stock_zh_index_daily(index_code)
    index_info.reset_index(inplace=True)

    index_info['date']=index_info['date'].astype(str)
    index_info['date']=index_info['date'].apply(lambda x:re.sub('-','',x))
    index_info=index_info[(index_info['date']>=startday)&(index_info['date']<=endday)]
    return index_info

#print(get_index_info_by_code('sh000300','20200101','20210314'))

def get_all_index_info_by_date(startday='19901219', endday='21000101'):
    engine = create_engine('mysql+pymysql://root:88888888@localhost:3308/stockdata')
    index_catalog=get_all_index_code_and_name()
    for i,indexs in index_catalog.iterrows():
        #print(indexs['index_code'],indexs['index_name'])
        index_info=get_index_info_by_code(indexs['index_code'],startday,endday)
        index_info.rename(columns={'date':'trade_date'},inplace=True)
        index_info.insert(1, 'index_code',indexs['index_code'])
        index_info.insert(2, 'index_name', indexs['index_name'])
        print(index_info)
        try:
            index_info.to_sql(name='index_info', con=engine, index=False, if_exists='append')
        except Exception as ee:
            logger = logging.getLogger()
            logger.error('get_index fileToMysql fialed', ee)
            traceback.print_exc()
    engine.dispose()

get_all_index_info_by_date('20210429','202100507')