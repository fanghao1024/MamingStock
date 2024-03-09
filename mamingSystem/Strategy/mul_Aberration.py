import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import printAnalyzers
import getTradeDate
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

class TurtleStrategy(bt.Strategy):
    # 默认参数
    params = (('long_period', 20),
              ('short_period', 10),
              ('printlog', True),
              ('ATR_period', 2),
              ('CASH_rate', 0.15),
              ('ATR_jiacang', 1),
              )

    def __init__(self):
        self.orderid = {}
        self.buyprice = {}
        self.buycomm = {}
        self.buy_size = {}
        self.buy_count = {}
        self.last_buy_cash = {}
        self.H_line={}
        self.L_line={}
        self.lines.TR={}
        self.lines.ATR={}
        self.lines.buy_signal={}
        self.lines.sell_signal={}

        self.inds = dict()
        for i, d in enumerate(self.datas):

            self.orderid[d] = None
            self.buyprice[d] = 0
            self.buycomm[d] = 0
            self.buy_size[d] = 0
            self.buy_count[d] = 0
            self.last_buy_cash[d] = 0

            self.inds[d] = dict()
            # 海龟交易法则中的唐奇安通道和平均波幅ATR
            #self.inds[d]['H_line']=bt.indicators.Highest(d.high(-1), period=self.p.long_period)
            self.H_line[d] = bt.indicators.Highest(d.high(-1), period=self.p.long_period)
            #self.inds[d]['L_line'] = bt.indicators.Highest(d.low(-1), period=self.p.short_period)
            self.L_line[d] = bt.indicators.Lowest(d.low(-1), period=self.p.short_period)
            #self.inds[d]['TR']=bt.indicators.Max((d.high(0) - d.low(0)),abs(d.close(-1) - d.high(0)),abs(d.close(-1) - d.low(0)))
            self.TR[d] = bt.indicators.Max((d.high(0) - d.low(0)),abs(d.close(-1) - d.high(0)),abs(d.close(-1) - d.low(0)))
            #self.inds[d]['ATR']=bt.indicators.SimpleMovingAverage(self.inds[d]['TR'], period=14)
            self.ATR[d] = bt.indicators.SimpleMovingAverage(self.lines.TR[d], period=14)
            # 价格与上下轨线的交叉
            #self.inds[d]['buy_signal'] = bt.ind.CrossOver(d.close(0), self.inds[d]['H_line'])
            self.buy_signal[d] = bt.ind.CrossOver(d.close(0), self.H_line[d])

            #self.inds[d]['sell_signal']=bt.ind.CrossOver(d.close(0), self.inds[d]['L_line'])
            self.sell_signal[d] = bt.ind.CrossOver(d.close(0), self.L_line[d])

    def next(self):


        for i, d in enumerate(self.datas):

            #if self.orderid[d]:
            #    return

            # 入场：价格突破上轨线且空仓时
            if self.buy_signal[d] > 0 and self.buy_count[d] == 0:
                self.buy_size[d] = self.broker.getcash() * self.p.CASH_rate / d.close[0]
                self.buy_size[d] = int(self.buy_size[d] / 100) * 100
                #self.p.stake = self.buy_size[d]
                print(d.datetime.date(0),'buy first','now total cash:', self.broker.getcash(),'plan to use cash:',
                      self.broker.getcash() * self.p.CASH_rate,'now close:',d.close[0],'buy size:',self.buy_size[d],'stock code:',d.stock_code[0])
                self.buy_count[d] = 1
                self.last_buy_cash[d] = self.buy_size[d] * d.close[0]
                self.buy(data=d,size=self.buy_size[d])
            # 加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
            elif d.close[0] > self.buyprice[d] + self.p.ATR_jiacang * self.ATR[d][0] and 0 < self.buy_count[d] <= 4:
                self.buy_size[d] = (self.last_buy_cash[d] / 2) / d.close[0]
                self.buy_size[d] = int(self.buy_size[d] / 100) * 100
                #self.sizer.p.stake = self.buy_size
                print(d.datetime.date(0), 'add: ', self.buy_count[d], 'now total cash:', self.broker.getcash(),'plan to use cash:',self.buy_size[d] * d.close[0],'buy size:',self.buy_size[d],
                      d.stock_code[0])
                self.buy(data=d,size=self.buy_size[d])
                #print(d.datetime.date(0), 'buy ', self.buy_count[d],' cash:',self.broker.getcash(),self.buy_size[d],d.stock_code[0])
                self.buy_count[d] += 1
                self.last_buy_cash[d] = self.buy_size[d] * d.close[0]

            # 离场：价格跌破下轨线且持仓时
            elif self.sell_signal[d] < 0 and self.buy_count[d] > 0:
                print(d.datetime.date(0), 'sell ', d.stock_code[0], 'size:', self.getposition(d).size)
                self.sell(data=d,size=self.getposition(d).size)
                self.buy_count[d] = 0
                self.last_buy_cash[d] = 0
            # 止损：价格跌破买入价的2个ATR且持仓时
            elif d.close < (self.buyprice[d] - self.p.ATR_period * self.ATR[d][0]) and self.buy_count[d] > 0:
                print(d.datetime.date(0), 'sell:', d.stock_code[0],'size:',self.getposition(d).size)
                self.sell(data=d,size=self.getposition(d).size)
                self.buy_count[d] = 0
                self.last_buy_cash[d] = 0
                print(d.datetime.date(0), 'sell:', d.stock_code[0],'size:',self.getposition(d).size)


    # 交易记录日志（默认不打印结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（默认不输出结果）
    '''
    def notify_order(self, order):
        print('notify_order')
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'买入:\n价格:{order.executed.price},成本:{order.executed.value},手续费:{order.executed.comm}，数量：{order.executed.size}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f'卖出:\n价格：{order.executed.price},成本: {order.executed.value},手续费{order.executed.comm}，数量：{order.executed.size}')

            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None
    '''
    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):

        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)


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
    #stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('600009', '20100101', '20210416')
    # stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')
    startday='20100101'
    endday='20201231'
    allTradeDays=getTradeDate.getPeriodTradeDate(startday,endday)
    allTradeDays.reset_index(inplace=True)
    stock_list = ['600036','601633', '300015', '601318', '600161','603755','300785','600030',\
                  '600161','002007','601088','601933','603596','603348','002074','002970','300496']

    for i,stock_code in enumerate(stock_list):
        stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq(stock_code, startday, endday)
        stock_daily_info = getTradeDate.fillTradeDate(stock_daily_info, startday, endday)
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
        cerebro.adddata(data,name=stock_code)

    # Add the strategy
    '''
    cerebro.addstrategy(AberrationStrategy,
                        period=args.period,
                        onlylong=True,
                        #csvcross=args.csvcross,
                        #stake=args.stake
                        )
    '''
    cerebro.addstrategy(TurtleStrategy)
    # cerebro.addsizer(TradeSizer)
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
    # cerebro.addanalyzer(GrossLeverage, _name='_grossLeverage')
    cerebro.addanalyzer(PositionsValue, _name='_positionsValue')
    cerebro.addanalyzer(PyFolio, _name='_pyFolio')
    # cerebro.addanalyzer(LogReturnsRolling, _name='_logReturnsRolling')
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
    trader_indicator, long_short_indicator = printAnalyzers.get_TradeAnalyzer(
        result.analyzers._tradeAnalyzer.get_analysis())
    print('_tradeAnalyzer:\n', trader_indicator, '\n', long_short_indicator)
    print('_calmar:\n', printAnalyzers.get_Carmar(result.analyzers._calmar.get_analysis()))
    print('_timedrawdown:\n', printAnalyzers.get_TimeDrawDown(result.analyzers._timeDrawDown.get_analysis()))
    # print('_grossLeverage:\n', printAnalyzers.get_GrossLeverageRatio(result.analyzers._grossLeverage.get_analysis()))
    #print('_positionsValue:\n', printAnalyzers.get_PositionValue(result.analyzers._positionsValue.get_analysis()))
    #print('_pyFolio:\n', printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[0], '\n',printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[1])
    # print('_logReturnsRolling:\n',printAnalyzers.get_LogReturnRolling(result.analyzers._logReturnsRolling.get_analysis()))
    print('_periodStats:\n', printAnalyzers.get_PeriodStats(result.analyzers._periodStats.get_analysis()))
    print('_returns:\n', printAnalyzers.get_Returns(result.analyzers._returns.get_analysis()))
    print('_sharpeRatio_A:\n', printAnalyzers.get_SharpeRatio_A(result.analyzers._sharpeRatio_A.get_analysis()))
    #print('_transactions:\n', printAnalyzers.get_Transactions(result.analyzers._transactions.get_analysis()))
    print('_VWR:\n', printAnalyzers.get_VWR(result.analyzers._VWR.get_analysis()))
    print('_SQN:\n', printAnalyzers.get_SQN(result.analyzers._SQN.get_analysis()))

    # Plot if requested

    #cerebro.plot(numfigs=1, volume=True, style='candle')


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


