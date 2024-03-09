import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import akshare as ak
import printAnalyzers
import matplotlib.pyplot as plt
import talib as ta

#get_daily_market_from_mysql.get_daily_market_qfq()

import argparse
import datetime
import numpy as np
import pandas as pd


pd.set_option('display.max_columns', None)
# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer, Calmar, TimeDrawDown, GrossLeverage,
                                  PositionsValue, PyFolio, LogReturnsRolling,
                                  PeriodStats, Returns, SharpeRatio_A, Transactions, VWR)

from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False



class TradeSizer(bt.Sizer):
    params = (('stake', 1000),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:

            return self.p.stake
        #如果发出卖出信号且有仓位，则卖出所有仓位
        position = self.broker.getposition(data)
        if not position.size:
            return 0
        else:
            return position.size
        return self.p.stake


class Acecommission(bt.CommInfoBase):
    params = (
        # 印花税，仅卖出收取千分之一
        ("stamp_duty", 0.001),
        ("commission", 0.0003),
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:
            return max(size * price * self.params.commission, 5)
        elif size < 0:
            return abs(size) * price * self.params.stamp_duty + max(size * price * self.params.commission, 5)


class Stock_data(btfeeds.PandasData):
    linesoverride = True  # discard usual OHLC structure
    # datetime must be present and last
    lines = ('datetime', 'stock_code', 'open', 'high', 'low', 'close', 'volume', 'outstanding_share', 'turnover')
    # datetime (always 1st) and then the desired order for
    params = (
        ('datetime', None),  # inherited from parent class
        ('stock_code', -1),  # default field pos 1
        ('open', -1),  # default field pos 2
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('outstanding_share', -1),
        ('turnover', -1),
    )


def FindCrossOver(Stockcode,startday,endday):
    args = parse_args()

    # Create a cerebro
    cerebro = bt.Cerebro()

    # Get the dates from the args
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y%m%d')
    todate = datetime.datetime.strptime(args.todate, '%Y%m%d')

    # Create the 1st data
    # stock_daily_info=get_daily_market_from_mysql.get_daily_market_qfq('600519','20000101','20210416')
    stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq(Stockcode, startday, endday)
    # stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')
    if stock_daily_info is None:
        return False

    stock_daily_info['trade_date'] = stock_daily_info['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    stock_daily_info['stock_code'] = stock_daily_info['stock_code'].astype(float)
    stock_daily_info['qfq_open'] = stock_daily_info['qfq_open'].astype(float)
    stock_daily_info['qfq_high'] = stock_daily_info['qfq_high'].astype(float)
    stock_daily_info['qfq_low'] = stock_daily_info['qfq_low'].astype(float)
    stock_daily_info['qfq_close'] = stock_daily_info['qfq_close'].astype(float)
    stock_daily_info['volume'] = stock_daily_info['volume'].astype(float)
    stock_daily_info['outstanding_share'] = stock_daily_info['outstanding_share'].astype(float)
    stock_daily_info['turnover'] = stock_daily_info['turnover'].astype(float)
    stock_daily_info.rename(columns={'trade_date': 'datetime', 'qfq_open': 'open', 'qfq_high': 'high', 'qfq_low': 'low',
                                     'qfq_close': 'close'}, inplace=True)
    stock_daily_info['datetime'] = pd.to_datetime(stock_daily_info['datetime'])
    stock_daily_info.set_index(['datetime'], inplace=True)
    #print(stock_daily_info)
    if len(stock_daily_info['close'])<3:
        return 0

    if stock_daily_info['close'][-3]<stock_daily_info['open'][-3] and stock_daily_info['close'][-2]<stock_daily_info['close'][-3] and \
		stock_daily_info['open'][-2]<stock_daily_info['close'][-3] and abs(stock_daily_info['close'][-2]-stock_daily_info['open'][-2])<abs(stock_daily_info['close'][-3]-stock_daily_info['open'][-3]) and \
		stock_daily_info['close'][-1]>stock_daily_info['open'][-1] and ((stock_daily_info['close'][-1]-stock_daily_info['close'][-3])/(stock_daily_info['open'][-3]-stock_daily_info['close'][-1]))>0.5:
        return 1



    return 0






def parse_args():
    parser = argparse.ArgumentParser(description='TimeReturn')

    # parser.add_argument('--data', '-d',default='../../datas/2005-2006-day-001.txt',help='data to add to the system')

    parser.add_argument('--fromdate', '-f',
                        default='20110101',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        default='20210410',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the Simple Moving Average')

    parser.add_argument('--onlylong', '-ol', action='store_true',
                        help='Do only long operations')

    parser.add_argument('--writercsv', '-wcsv', action='store_true',
                        help='Tell the writer to produce a csv stream')

    parser.add_argument('--csvcross', action='store_true',
                        help='Output the CrossOver signals to CSV')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tframe', default='years', required=False,
                       choices=['days', 'weeks', 'months', 'years'],
                       help='TimeFrame for the returns/Sharpe calculations')

    group.add_argument('--legacyannual', action='store_true',
                       help='Use legacy annual return analyzer')

    parser.add_argument('--cash', default=500000, type=int,
                        help='Starting Cash')

    parser.add_argument('--comm', default=2, type=float,
                        help='Commission for operation')

    parser.add_argument('--mult', default=10, type=int,
                        help='Multiplier for futures')

    parser.add_argument('--margin', default=1000.0, type=float,
                        help='Margin for each future')

    parser.add_argument('--stake', default=1000, type=int,
                        help='Stake to apply in each operation')

    return parser.parse_args()

if __name__ == '__main__':

    startday='20211120'
    endday='20211126'



    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    mark = False
    stocklist=[]
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        # if mark == False and str(code) != '300522':
        #    continue
        # else:
        #    mark = True
        if str(code) == '689009' or str(code) == '688616':
            continue
        marks=FindCrossOver(code,startday,endday)
        if marks==1:
            print('find one down:',code,name)
            stocklist.append(code)

    print('-----stock list black cloud top-----')
    print(stocklist)




