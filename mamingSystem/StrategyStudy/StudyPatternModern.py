import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import akshare as ak
import printAnalyzers
import matplotlib.pyplot as plt
import talib as ta
import os
from openpyxl import load_workbook

#get_daily_market_from_mysql.get_daily_market_qfq()

import argparse
import datetime
import numpy as np
import pandas as pd


pd.set_option('display.max_columns', None)


from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 通过pattern_name设定要跑的指标，在此处设定指标名称
pattern_names = 'CDL3OUTSIDE'
pattern={'CDL2CROWS':'两只乌鸦','CDL3BLACKCROWS':'三只乌鸦','CDL3INSIDE':'三内部上涨和下跌','CDL3LINESTRIKE':'三线打击','CDL3OUTSIDE':'三外部上涨和下跌',\
		 'CDL3STARSINSOUTH':'南方三星','CDL3WHITESOLDIERS':'三个白兵','CDLABANDONEDBABY':'弃婴','CDLADVANCEBLOCK':'大敌当前','CDLBELTHOLD':'捉腰带线',\
		 'CDLBREAKAWAY':'脱离','CDLCLOSINGMARUBOZU':'收盘缺影线','CDLCONCEALBABYSWALL':'藏婴吞没','CDLCOUNTERATTACK':'反击线','CDLDARKCLOUDCOVER':'乌云压顶',\
		 'CDLDOJI':'十字','CDLDOJISTAR':'十字星','CDLDRAGONFLYDOJI':'蜻蜓十字/T形十字','CDLENGULFING':'吞噬模式','CDLEVENINGDOJISTAR':'十字暮星',\
		 'CDLEVENINGSTAR':'暮星','CDLGAPSIDESIDEWHITE':'向上/下跳空并列阳线','CDLGRAVESTONEDOJI':'墓碑十字/倒T十字','CDLHAMMER':'锤头',\
		 'CDLHANGINGMAN':'上吊线','CDLHARAMI':'母子线','CDLHARAMICROSS':'十字孕线','CDLHIGHWAVE':'风高浪大线','CDLHIKKAKE':'陷阱',\
		 'CDLHIKKAKEMOD':'修正陷阱','CDLHOMINGPIGEON':'家鸽','CDLIDENTICAL3CROWS':'三胞胎乌鸦','CDLINNECK':'颈内线','CDLINVERTEDHAMMER':'倒锤头',\
		 'CDLKICKING':'反冲形态','CDLKICKINGBYLENGTH':'由较长缺影线决定的反冲形态','CDLLADDERBOTTOM':'梯底','CDLLONGLEGGEDDOJI':'长脚十字','CDLLONGLINE':'长蜡烛',\
		 'CDLMARUBOZU':'光头光脚/缺影线','CDLMATCHINGLOW':'相同低价','CDLMATHOLD':'铺垫','CDLMORNINGDOJISTAR':'十字晨星','CDLMORNINGSTAR':'晨星',\
		 'CDLONNECK':'颈上线','CDLPIERCING':'刺透形态','CDLRICKSHAWMAN':'黄包车夫','CDLRISEFALL3METHODS':'上升/下降三法','CDLSEPARATINGLINES':'分离线',\
		 'CDLSHOOTINGSTAR':'射击之星','CDLSHORTLINE':'短蜡烛','CDLSPINNINGTOP':'纺锤','CDLSTALLEDPATTERN':'停顿形态','CDLSTICKSANDWICH':'条形三明治',\
		 'CDLTAKURI':'探水竿','CDLTASUKIGAP':'跳空并列阴阳线','CDLTHRUSTING':'插入','CDLTRISTAR':'三星','CDLUNIQUE3RIVER':'奇特三河床',\
		 'CDLUPSIDEGAP2CROWS':'向上跳空的两只乌鸦','CDLXSIDEGAP3METHODS':'上升/下降跳空三法'}


def FindTAPattern(Stockcode,startday,endday):

    # Create the 1st data
    # stock_daily_info=get_daily_market_from_mysql.get_daily_market_qfq('600519','20000101','20210416')
    stock_daily_info = get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf(Stockcode, startday, endday)
    # stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')
    if stock_daily_info is None:
        return False

    #stock_daily_info['trade_date'] = stock_daily_info['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    #stock_daily_info['stock_code'] = stock_daily_info['stock_code'].astype(float)
    stock_daily_info['bfq_open'] = stock_daily_info['bfq_open'].astype(float)
    stock_daily_info['bfq_high'] = stock_daily_info['bfq_high'].astype(float)
    stock_daily_info['bfq_low'] = stock_daily_info['bfq_low'].astype(float)
    stock_daily_info['bfq_close'] = stock_daily_info['bfq_close'].astype(float)
    stock_daily_info['volume'] = stock_daily_info['volume'].astype(float)
    stock_daily_info['deal'] = stock_daily_info['deal'].astype(float)
    stock_daily_info['turnover'] = stock_daily_info['turnover'].astype(float)
    stock_daily_info.rename(columns={'trade_date': 'datetime', 'bfq_open': 'open', 'bfq_high': 'high', 'bfq_low': 'low',
                                     'bfq_close': 'close'}, inplace=True)
    #stock_daily_info['datetime'] = pd.to_datetime(stock_daily_info['datetime'])
    #stock_daily_info.set_index(['datetime'], inplace=True)
    #print(stock_daily_info)

    # 计算N天后涨跌幅
    for i in range(1,11):
        stock_daily_info[str(i)]=(stock_daily_info['close'].shift(-i)/stock_daily_info['close']-1)*100

    #print(stock_daily_info)
    # 计算技术指标。不同指标此处需要参数可能不同，需要修改。
    for pattern_name in pattern:

        stock_daily_info[pattern[pattern_name]] = getattr(ta, pattern_name)(stock_daily_info['open'].values, stock_daily_info['high'].values,
														stock_daily_info['low'].values, stock_daily_info['close'].values)
    #print(stock_daily_info)
     # 去除N天后涨跌幅为空的情况
    for i in range(1,11):
        stock_daily_info= stock_daily_info[stock_daily_info[str(i)].notnull()]
    print(stock_daily_info)

    return stock_daily_info
        # 合并数据


if __name__ == '__main__':

    startday='19901024'
    endday='20220118'

    file1='../data/StockFactor/'
    file2='../data/TechAnalyFactor/'

    #for pattern_name in pattern:
    #    print(output.groupby(pattern[pattern_name])[[str(i)  for i in range(1, 11)]].describe())



    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    mark = False

    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)

        marks = FindTAPattern(code, startday, endday)
        print(marks)
        filename = code + '.csv'

        marks.to_csv(file1 + filename,index=False)
        for pattern_name in pattern:
            if len(marks[marks[pattern[pattern_name]] != 0]) > 0:
                if os.path.exists(file2 + pattern_name + '.csv') == False:
                    marks[marks[pattern[pattern_name]] != 0].to_csv(file2 + pattern_name+'.csv', index=False)
                else:
                    marks[marks[pattern[pattern_name]] != 0].to_csv(file2 + pattern_name+'.csv', index=False,header=False,mode='a')

'''
                    df1 = pd.DataFrame(pd.read_excel(file2 + pattern_name + '.xlsx'))
                    book = load_workbook(file2 + pattern_name + '.xlsx')
                    writer = pd.ExcelWriter(file2 + pattern_name + '.xlsx', engine='openpyxl')
                    writer.book = book
                    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
                    df_rows = df1.shape[0]
                    marks[marks[pattern[pattern_name]] != 0].to_excel(writer, startrow=df_rows + 1, index=False,
                                                                      header=False)
                    writer.save()  # 保存
                    '''







