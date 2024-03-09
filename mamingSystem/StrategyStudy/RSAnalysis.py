import sys
import os
os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
sys.path.append('../TechAnalyFactor')

import get_daily_index_market_from_mysql
import get_daily_industry_market_from_mysql
import get_daily_market_from_mysql
import get_daily_ETF_market_from_mysql
import RSFactor


func_dist={'stock':get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf,\
    'index':get_daily_index_market_from_mysql.get_daily_index_market_information,\
        'board':get_daily_industry_market_from_mysql.get_daily_board_market_bfq_from_dfcf,\
            'ETF':get_daily_ETF_market_from_mysql.get_ETF_daily_market_information,}

def fun_none(a,b,c):
    print('wrong type')
    return None

import printAnalyzers
import matplotlib.pyplot as plt



# get_daily_market_from_mysql.get_daily_market_qfq()

import argparse
import datetime
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


class SimpleMovingAverage1(bt.Indicator):
    lines = ('sma',)
    params = (('period', 1),)
    plotinfo = dict(subplot=True)

    def next(self):
        datasum = self.data.get(size=self.p.period)
        self.lines.sma[0] = datasum



class RSStrategy(bt.Strategy):
    '''#平滑异同移动平均线MACD
        DIF(蓝线): 计算12天平均和26天平均的差，公式：EMA(C,12)-EMA(c,26)
       Signal(DEM或DEA或MACD) (红线): 计算macd9天均值，公式：Signal(DEM或DEA或MACD)：EMA(MACD,9)
        Histogram (柱): 计算macd与signal的差值，公式：Histogram：MACD-Signal

        period_me1=12
        period_me2=26
        period_signal=9

        macd = ema(data, me1_period) - ema(data, me2_period)
        signal = ema(macd, signal_period)
        histo = macd - signal

    '''
    params = (
        ('shortTime', 19),
        ('longTime', 39),
        ('other', 10),
    )

    def __init__(self):
        # sma源码位于indicators\macd.py
        # 指标必须要定义在策略类中的初始化函数中
        '''
        self.my=TengLuoFactor.TengLuoFactor_Bolton('CYB','20200101', '20220118')
        self.my['trade_date'] = self.my['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        self.my.rename(columns={'trade_date': 'datetime'}, inplace=True)
        self.my['datetime'] = pd.to_datetime(self.my['datetime'])
        self.my.set_index(['datetime'], inplace=True)
        print(self.my)
        '''
        #self.Bolton=bt.ind.SMA(self.my)

        self.dataclose = self.datas[0].close

        RS = bt.ind.SMA(self.datas[0].RS, period=1)
        RS.plotinfo.plotname = 'RS'
        RS.plotinfo.subplot = True

        RS1=bt.ind.SMA(self.datas[0].RS,period=10)
        RS1.plotinfo.plotname = 'RS_10MA'
        RS1.plotinfo.subplot = True
        RS1.plotinfo.plotmaster = RS
        RS1.plotinfo.sameaxis = True

        self.order = None
        self.buyprice = None
        self.buycomm = None

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_cashvalue(self, cash, value):
        self.log('Cash %s Value %s' % (cash, value))

    def notify_order(self, order):
        print(type(order), 'Is Buy ', order.isbuy())
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):

        if self.order:  # 检查是否有指令等待执行,
            return

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if we are in the market


class TradeSizer(bt.Sizer):
    params = (('stake', 1000),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return self.p.stake
        # 如果发出卖出信号且有仓位，则卖出所有仓位
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


class Index_data(btfeeds.PandasData):
    linesoverride = True  # discard usual OHLC structure
    # datetime must be present and last
    lines = ('datetime', 'index_code', 'open', 'high', 'low', 'close', 'volume', 'RS',)
    # datetime (always 1st) and then the desired order for
    params = (
        ('datetime', None),  # inherited from parent class
        ('index_code', -1),  # default field pos 1
        ('open', -1),  # default field pos 2
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('RS',-1),
    )


def runstrategy():

    startday = '20170101'
    endday = '20220119'

    codeA = '600519'
    typeA = 'stock'
    codeB = '000001'
    typeB = 'index'
    # Create a cerebro
    cerebro = bt.Cerebro()

    # Create the 1st data
    # stock_daily_info=get_daily_market_from_mysql.get_daily_market_qfq('600519','20000101','20210416')

    A = func_dist.get(typeA, fun_none)(codeA, startday, endday)
    B = func_dist.get(typeB, fun_none)(codeB, startday, endday)

    # stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')
    
    A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A['open'] = A['open'].astype(float)
    A['high'] = A['high'].astype(float)
    A['low'] = A['low'].astype(float)
    A['close'] = A['close'].astype(float)
    A['volume'] = A['volume'].astype(float)
    A = A[['trade_date','open','high','low','close','volume']]
    A.rename(columns={'trade_date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)

    B['trade_date'] = B['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    B['open'] = B['open'].astype(float)
    B['high'] = B['high'].astype(float)
    B['low'] = B['low'].astype(float)
    B['close'] = B['close'].astype(float)
    B['volume'] = B['volume'].astype(float)
    B = B[['trade_date', 'open', 'high', 'low', 'close', 'volume']]
    B.rename(columns={'trade_date': 'datetime'}, inplace=True)
    B['datetime'] = pd.to_datetime(B['datetime'])
    B.set_index(['datetime'], inplace=True)
    print(typeA,codeA,typeB,codeB,startday,endday)
    C=RSFactor.RSFactor(codeA,typeA,codeB,typeB,startday,endday)

    A=A.join(C)
    B=B.join(C)


    data0 = Index_data(dataname=A, nocase=True, )
    data0.plotinfo.plotlog = True

    data1 = Index_data(dataname=B, nocase=True, )
    data1.plotinfo.plotlog = True
    # data = bt.feeds.PandasData(dataname=stock_daily_info,nocase=True,)


    cerebro.addstrategy(
        RSStrategy,
        shortTime=19,
        longTime=39,
        other=10
    )
    # Add the 1st data to cerebro
    cerebro.adddata(data0,name=typeA+codeA)
    cerebro.adddata(data1, name=typeB+codeB)

    # Add the strategy
    '''
    cerebro.addstrategy(AberrationStrategy,
                        period=args.period,
                        onlylong=True,
                        #csvcross=args.csvcross,
                        #stake=args.stake
                        )
    '''
    # cerebro.addstrategy(MACDStrategy)
    # cerebro.addsizer(TradeSizer)
    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(1000000)

    cerebro.broker.addcommissioninfo(Acecommission(stamp_duty=0.001, commission=0.0003))
    # Add the commission - only stocks like a for each operation
    # cerebro.broker.setcommission(commission=args.comm,mult=args.mult,margin=args.margin)

    tframes = dict(
        days=bt.TimeFrame.Days,
        weeks=bt.TimeFrame.Weeks,
        months=bt.TimeFrame.Months,
        years=bt.TimeFrame.Years)

    # Add the Analyzers
    '''
    cerebro.addanalyzer(AnnualReturn, _name='_annualReturn')
    # cerebro.addanalyzer(SharpeRatio, legacyannual=True,_name='_sharpeRatio')
    cerebro.addanalyzer(Calmar, _name='_calmar')
    cerebro.addanalyzer(TimeDrawDown, _name='_timeDrawDown')
    #cerebro.addanalyzer(GrossLeverage, _name='_grossLeverage')
    cerebro.addanalyzer(PositionsValue, _name='_positionsValue')
    cerebro.addanalyzer(PyFolio, _name='_pyFolio')
    #cerebro.addanalyzer(LogReturnsRolling, _name='_logReturnsRolling')
    cerebro.addanalyzer(PeriodStats, _name='_periodStats')
    cerebro.addanalyzer(Returns, _name='_returns')
    cerebro.addanalyzer(SharpeRatio_A, _name='_sharpeRatio_A')
    cerebro.addanalyzer(Transactions, _name='_transactions')

    cerebro.addanalyzer(TimeReturn, timeframe=tframes[args.tframe], _name='_timeReturn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="_drawDown")
    cerebro.addanalyzer(TradeAnalyzer, _name='_tradeAnalyzer')
    '''
    cerebro.addanalyzer(VWR, _name='_VWR')
    cerebro.addanalyzer(SQN, _name='_SQN')
    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, rounding=4)

    # And run it
    results = cerebro.run()
    result = results[0]
    '''
    print(printAnalyzers.get_AnnualReturn(result.analyzers._annualReturn.get_analysis()))
    # print('_sharpeRatio:\n',printAnalyzers.get_SharpeRatio(result.analyzers._sharpeRatio.get_analysis()))
    print('_timeReturn:\n', printAnalyzers.get_TimeReturn(result.analyzers._timeReturn.get_analysis()))
    print('_drawDown:\n', printAnalyzers.get_DrawDown(result.analyzers._drawDown.get_analysis()))
    #trader_indicator, long_short_indicator = printAnalyzers.get_TradeAnalyzer(result.analyzers._tradeAnalyzer.get_analysis())
    #print('_tradeAnalyzer:\n', trader_indicator, '\n', long_short_indicator)
    print('_calmar:\n', printAnalyzers.get_Carmar(result.analyzers._calmar.get_analysis()))
    print('_timedrawdown:\n', printAnalyzers.get_TimeDrawDown(result.analyzers._timeDrawDown.get_analysis()))
    #print('_grossLeverage:\n', printAnalyzers.get_GrossLeverageRatio(result.analyzers._grossLeverage.get_analysis()))
    print('_positionsValue:\n', printAnalyzers.get_PositionValue(result.analyzers._positionsValue.get_analysis()))
    print('_pyFolio:\n', printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[0], '\n',
          printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[1])
    #print('_logReturnsRolling:\n',printAnalyzers.get_LogReturnRolling(result.analyzers._logReturnsRolling.get_analysis()))
    print('_periodStats:\n', printAnalyzers.get_PeriodStats(result.analyzers._periodStats.get_analysis()))
    print('_returns:\n', printAnalyzers.get_Returns(result.analyzers._returns.get_analysis()))
    print('_sharpeRatio_A:\n', printAnalyzers.get_SharpeRatio_A(result.analyzers._sharpeRatio_A.get_analysis()))
    print('_transactions:\n', printAnalyzers.get_Transactions(result.analyzers._transactions.get_analysis()))
    '''
    print('_VWR:\n', printAnalyzers.get_VWR(result.analyzers._VWR.get_analysis()))
    print('_SQN:\n', printAnalyzers.get_SQN(result.analyzers._SQN.get_analysis()))

    # Plot if requested

    cerebro.plot(numfigs=1, volume=True, style='candle')


if __name__ == '__main__':

    runstrategy()
