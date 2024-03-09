import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import printAnalyzers
import matplotlib.pyplot as plt

#get_daily_market_from_mysql.get_daily_market_qfq()

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

class MACDStrategy(bt.Strategy):
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
    params =(
        ('p1',8),
        ('p2',18),
        ('p3',18),
    )

    def __init__(self):
        # sma源码位于indicators\macd.py
        # 指标必须要定义在策略类中的初始化函数中
        self.dataclose = self.datas[0].close
        macd = bt.ind.MACDAll(self.dataclose,period_me1=self.p.p1,period_me2=self.p.p2,period_signal=self.p.p3)
        self.macd = macd.macd
        self.signal = macd.signal
        self.histo1=macd.histo
        self.histo = bt.ind.MACDHisto(self.dataclose,period_me1=self.p.p1,period_me2=self.p.p2,period_signal=self.p.p3)

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

        if self.order: # 检查是否有指令等待执行,
            return

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if we are in the market
        print(self.datas[0].datetime.date(),'macd:',self.macd[0],'signal:',self.signal[0],'histo1:',self.histo1[0])
        if not self.getposition(self.datas[0]):

            # self.data.close是表示收盘价
            # 收盘价大于histo，买入
            if self.macd[0] > 0 and self.signal[0] > 0 and self.histo1[0] > 0:
                self.log('BUY CREATE,{}'.format(self.dataclose[0]))
                total_value = self.broker.getvalue()
                # 1手=100股，满仓买入
                ss = int((total_value / 100) / self.datas[0].close[0]) * 100
                self.order = self.buy(self.datas[0],size=ss)

        else:

            # 收盘价小于等于histo，卖出
            if self.macd[0] <= 0 or self.signal[0] <= 0 or self.histo1[0] <= 0:
                self.log('SELL CREATE,{}'.format(self.dataclose[0]))
                self.log('Pos size %s' % self.position.size)
                self.order = self.close(self.datas[0])


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


def runstrategy():
    args = parse_args()

    # Create a cerebro
    cerebro = bt.Cerebro()

    # Get the dates from the args
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y%m%d')
    todate = datetime.datetime.strptime(args.todate, '%Y%m%d')

    # Create the 1st data
    # stock_daily_info=get_daily_market_from_mysql.get_daily_market_qfq('600519','20000101','20210416')
    stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('603949', '20170101', '20211026')
    # stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')


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

    print(stock_daily_info)
    data = Stock_data(dataname=stock_daily_info, nocase=True, )

    # data = bt.feeds.PandasData(dataname=stock_daily_info,nocase=True,)

    # Add the 1st data to cerebro
    cerebro.adddata(data)

    # Add the strategy
    '''
    cerebro.addstrategy(AberrationStrategy,
                        period=args.period,
                        onlylong=True,
                        #csvcross=args.csvcross,
                        #stake=args.stake
                        )
    '''
    cerebro.addstrategy(MACDStrategy)
    #cerebro.addsizer(TradeSizer)
    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(args.cash)

    cerebro.broker.addcommissioninfo(Acecommission(stamp_duty=0.001, commission=0.0003))
    # Add the commission - only stocks like a for each operation
    # cerebro.broker.setcommission(commission=args.comm,mult=args.mult,margin=args.margin)

    tframes = dict(
        days=bt.TimeFrame.Days,
        weeks=bt.TimeFrame.Weeks,
        months=bt.TimeFrame.Months,
        years=bt.TimeFrame.Years)

    # Add the Analyzers

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
    cerebro.addanalyzer(VWR, _name='_VWR')
    cerebro.addanalyzer(SQN, _name='_SQN')
    cerebro.addanalyzer(TimeReturn, timeframe=tframes[args.tframe], _name='_timeReturn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="_drawDown")
    cerebro.addanalyzer(TradeAnalyzer, _name='_tradeAnalyzer')

    # cerebro.addwriter(bt.WriterFile, csv=args.writercsv, rounding=4)

    # And run it
    results = cerebro.run()
    result = results[0]
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
    print('_VWR:\n', printAnalyzers.get_VWR(result.analyzers._VWR.get_analysis()))
    print('_SQN:\n', printAnalyzers.get_SQN(result.analyzers._SQN.get_analysis()))

    # Plot if requested

    cerebro.plot(numfigs=1, volume=True,style='candle')


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
    runstrategy()
