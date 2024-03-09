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

class AberrationStrategy(bt.Strategy):
    # 默认参数
    params = (('long_period', 20),
              ('short_period', 10),
              ('printlog', True),
              ('ATR_period',2),
              ('CASH_rate',0.4),
              ('ATR_jiacang',1),
              ('ATR_period',14),
              )

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.buy_size = 0
        self.buy_count = 0
        self.last_buy_cash=0
        # 海龟交易法则中的唐奇安通道和平均波幅ATR
        self.H_line = bt.indicators.Highest(self.data.high(-1), period=self.p.long_period)
        #print('self.H_line:',self.H_line)
        self.L_line = bt.indicators.Lowest(self.data.low(-1), period=self.p.short_period)
        self.lines.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))
        self.lines.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=self.p.ATR_period)
        # 价格与上下轨线的交叉
        self.lines.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.lines.sell_signal = bt.ind.CrossOver(self.data.close(0), self.L_line)

    def next(self):
        if self.order:
            return
        # 入场：价格突破上轨线且空仓时
        if self.buy_signal > 0 and self.buy_count == 0:
            self.buy_size = self.broker.getcash() * self.p.CASH_rate / self.data.close[0]
            self.buy_size = int(self.buy_size / 100) * 100
            self.p.stake = self.buy_size
            print(self.datas[0].datetime.date(0), ' cash:', self.broker.getcash(),self.broker.getcash() * self.p.CASH_rate,self.data.close[0],self.buy_size)
            self.buy_count = 1
            self.last_buy_cash=self.buy_size * self.data.close[0]
            self.order = self.buy(size=self.buy_size)
        # 加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + self.p.ATR_jiacang * self.ATR[0] and 0 < self.buy_count <= 4:
            self.buy_size = (self.last_buy_cash/2) / self.data.close[0]
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            self.buy_count += 1
            self.last_buy_cash = self.buy_size * self.data.close[0]
        # 离场：价格跌破下轨线且持仓时
        elif self.sell_signal < 0 and self.buy_count > 0:
            self.order = self.sell(size=self.broker.getposition(self.data).size)
            self.buy_count = 0
            self.last_buy_cash =0
        # 止损：价格跌破买入价的2个ATR且持仓时
        elif self.data.close < (self.buyprice - self.p.ATR_period * self.ATR[0]) and self.buy_count > 0:
            self.order = self.sell(size=self.broker.getposition(self.data).size)
            self.buy_count = 0
            self.last_buy_cash =0

    # 交易记录日志（默认不打印结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},成本:{order.executed.value},手续费:{order.executed.comm}，数量：{order.executed.size}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},成本: {order.executed.value},手续费{order.executed.comm}，数量：{order.executed.size}')

            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)

class Abbration(bt.Strategy):

    # 策略的参数
    params = (("boll_period", 40),
              ("boll_mult", 1),
              )

    # log相应的信息
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])
        print('{}, {}'.format(dt.isoformat(), txt))

    # 初始化策略的数据
    def __init__(self):
        # 计算布林带指标，大名鼎鼎的布林带策略
        self.boll_indicator = bt.indicators.BollingerBands(self.datas[0].close, period=self.p.boll_period)

        # 保存交易状态
        self.marketposition = 0

    def prenext(self):
        # 由于期货数据有几千个，每个期货交易日期不同，并不会自然进入next
        # 需要在每个prenext中调用next函数进行运行
        # self.next()
        pass

    # 在next中添加相应的策略逻辑
    def next(self):
        # 每次运行一次，bar_num自然加1,并更新交易日
        self.current_datetime = bt.num2date(self.datas[0].datetime[0])

        # 数据
        data = self.datas[0]
        # 指标值
        # 布林带上轨
        top = self.boll_indicator.top
        # 布林带下轨
        bot = self.boll_indicator.bot
        # 布林带中轨
        mid = self.boll_indicator.mid

        #if data.close[0] > top[0] and data.close[-1] < top[-1]:
        #    print(self.current_datetime,self.marketposition)

        # 开多
        if self.marketposition == 0 and data.close[0] > top[0] and data.close[-1] < top[-1]:
            # 获取一倍杠杆下单的手数
            close = data.close[0]
            total_value = self.broker.getcash()
            lots = total_value / close
            lots=int(lots/100)*100
            self.buy(data, size=lots)
            self.marketposition = 1
        elif (self.marketposition != 0 and data.close[0] < mid[0] and data.close[-1] > mid[-1]):
            self.close()
            self.marketposition = 0

        '''          
                if self.marketposition == 0 and data.close[0] > top[0] and data.close[-1] < top[-1]:
                    # 获取一倍杠杆下单的手数
                    close = data.close[0]
                    total_value = self.broker.getcash()
                    lots = total_value / close
                    lots=int(lots/100)*100
                    self.buy(data, size=lots)
                    self.marketposition = 1
        
                elif self.marketposition == 1 and data.close[0] > top[0] and data.close[-1] < top[-1]:
                    # 获取一倍杠杆下单的手数
                    close = data.close[0]
                    total_value = self.broker.getcash() / 2
                    lots = total_value / close
                    lots = int(lots / 100) * 100
                    self.buy(data, size=lots)
                    self.marketposition = 2
        
                elif self.marketposition == 2 and data.close[0] > top[0] and data.close[-1] < top[-1]:
                    # 获取一倍杠杆下单的手数
                    close = data.close[0]
                    total_value = self.broker.getcash()
                    lots = total_value / close
                    lots = int(lots / 100) * 100
                    self.buy(data, size=lots)
                    self.marketposition = 3
        
        
                elif (self.marketposition != 0 and data.close[0] < mid[0] and data.close[-1] > mid[-1]):
                    self.close()
                    self.marketposition = 0
        '''
# 开空
        '''
        if self.marketposition == 0 and data.close[0] < bot[0] and data.close[-1] > bot[-1]:
            # 获取一倍杠杆下单的手数
            info = self.broker.getcommissioninfo(data)
            symbol_multi = info.p.mult
            close = data.close[0]
            total_value = self.broker.getvalue()
            lots = total_value / (symbol_multi * close)
            self.sell(data, size=lots)
            self.marketposition = -1
        '''

        # 平多


        # 平空
        if self.marketposition == -1 and data.close[0] > mid[0] and data.close[-1] < mid[-1]:
            self.close()
            self.marketposition = 0

    # def notify_order(self, order):

    #     if order.status in [order.Submitted, order.Accepted]:
    #         return

    #     if order.status == order.Rejected:
    #         self.log(f"Rejected : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Margin:
    #         self.log(f"Margin : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Cancelled:
    #         self.log(f"Concelled : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Partial:
    #         self.log(f"Partial : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Completed:
    #         if order.isbuy():
    #             self.log(f" BUY : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")

    #         else:  # Sell
    #             self.log(f" SELL : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")

    # def notify_trade(self, trade):
    #     # 一个trade结束的时候输出信息
    #     if trade.isclosed:
    #         self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
    #                         trade.getdataname(),trade.pnl, trade.pnlcomm))
    #         # self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])

    #     if trade.isopen:
    #         self.log('open symbol is : {} , price : {} ' .format(
    #                         trade.getdataname(),trade.price))

    # def stop(self):

    #     pass

class ATRAbbration(bt.Strategy):

    # 策略的参数
    params = (("ATR_period", 20),
              ("ATR_range", 0.5),
              ("SMA_range",20),
              )

    # log相应的信息
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])
        print('{}, {}'.format(dt.isoformat(), txt))

    # 初始化策略的数据
    def __init__(self):
        # 计算布林带指标，大名鼎鼎的布林带策略
        self.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                          abs(self.data.close(-1) - self.data.high(0)),
                                          abs(self.data.close(-1) - self.data.low(0)))
        self.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=self.p.ATR_period)

        self.high=self.data.close+self.ATR(-1)*self.p.ATR_range
        self.low=self.data.close-self.ATR(-1)*self.p.ATR_range

        self.mid=bt.indicators.MovingAverageSimple(self.data.close,period=self.p.SMA_range)

        # 保存交易状态
        self.marketposition = 0

    def prenext(self):
        # 由于期货数据有几千个，每个期货交易日期不同，并不会自然进入next
        # 需要在每个prenext中调用next函数进行运行
        # self.next()
        pass

    # 在next中添加相应的策略逻辑
    def next(self):
        # 每次运行一次，bar_num自然加1,并更新交易日
        self.current_datetime = bt.num2date(self.datas[0].datetime[0])

        # 数据
        data = self.datas[0]
        #if data.close[0] > top[0] and data.close[-1] < top[-1]:
        #    print(self.current_datetime,self.marketposition)
        print('date:',self.current_datetime)
        print('high:',self.high[0])
        print('low:', self.low[0])
        print('mid:', self.mid[0])
        print('close:', data.close[0])

        # 开多
        if self.marketposition == 0 and data.close[0] > self.high[0] and data.close[-1] < self.high[-1]:
            # 获取一倍杠杆下单的手数
            close = data.close[0]
            total_value = self.broker.getcash()
            lots = total_value / close
            lots=int(lots/100)*100
            self.buy(data, size=lots)
            self.marketposition = 1

        elif self.marketposition == 1 and data.close[0] > self.high[0] and data.close[-1] < self.high[-1]:
            # 获取一倍杠杆下单的手数
            close = data.close[0]
            total_value = self.broker.getcash() / 2
            lots = total_value / close
            lots = int(lots / 100) * 100
            self.buy(data, size=lots)
            self.marketposition = 2

        elif self.marketposition == 2 and data.close[0] > self.high[0] and data.close[-1] < self.high[-1]:
            # 获取一倍杠杆下单的手数
            close = data.close[0]
            total_value = self.broker.getcash()
            lots = total_value / close
            lots = int(lots / 100) * 100
            self.buy(data, size=lots)
            self.marketposition = 3


        elif (self.marketposition != 0 and data.close[0] < self.mid[0] and data.close[-1] > self.mid[-1]):
            self.close(data)
            self.marketposition = 0

        # 开空
        '''
        if self.marketposition == 0 and data.close[0] < bot[0] and data.close[-1] > bot[-1]:
            # 获取一倍杠杆下单的手数
            info = self.broker.getcommissioninfo(data)
            symbol_multi = info.p.mult
            close = data.close[0]
            total_value = self.broker.getvalue()
            lots = total_value / (symbol_multi * close)
            self.sell(data, size=lots)
            self.marketposition = -1
        '''

        # 平多


        # 平空
        if self.marketposition == -1 and data.close[0] > self.mid[0] and data.close[-1] < self.mid[-1]:
            self.close()
            self.marketposition = 0

    # def notify_order(self, order):

    #     if order.status in [order.Submitted, order.Accepted]:
    #         return

    #     if order.status == order.Rejected:
    #         self.log(f"Rejected : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Margin:
    #         self.log(f"Margin : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Cancelled:
    #         self.log(f"Concelled : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Partial:
    #         self.log(f"Partial : order_ref:{order.ref}  data_name:{order.p.data._name}")

    #     if order.status == order.Completed:
    #         if order.isbuy():
    #             self.log(f" BUY : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")

    #         else:  # Sell
    #             self.log(f" SELL : data_name:{order.p.data._name} price : {order.executed.price} , cost : {order.executed.value} , commission : {order.executed.comm}")

    # def notify_trade(self, trade):
    #     # 一个trade结束的时候输出信息
    #     if trade.isclosed:
    #         self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
    #                         trade.getdataname(),trade.pnl, trade.pnlcomm))
    #         # self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])

    #     if trade.isopen:
    #         self.log('open symbol is : {} , price : {} ' .format(
    #                         trade.getdataname(),trade.price))

    # def stop(self):

    #     pass


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
    stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('605117', '20100101', '20211024')
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
    cerebro.addstrategy(Abbration)
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

class TurtleStrategy1(bt.Strategy):
    # 默认参数
    params = (('long_period', 20),
              ('short_period', 10),
              ('printlog', False),
              ('ATR_period',2),
              ('CASH_rate',0.05))

    def __init__(self):
        self.order = None
        self.buyprice = 0
        self.buycomm = 0
        self.buy_size = 0
        self.buy_count = 0
        # 海龟交易法则中的唐奇安通道和平均波幅ATR
        self.H_line = bt.indicators.Highest(self.data.high(-1), period=self.p.long_period)
        #print('self.H_line:',self.H_line)
        self.L_line = bt.indicators.Lowest(self.data.low(-1), period=self.p.short_period)
        self.lines.TR = bt.indicators.Max((self.data.high(0) - self.data.low(0)),
                                    abs(self.data.close(-1) - self.data.high(0)),
                                    abs(self.data.close(-1) - self.data.low(0)))
        self.lines.ATR = bt.indicators.SimpleMovingAverage(self.TR, period=14)
        # 价格与上下轨线的交叉
        self.lines.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.lines.sell_signal = bt.ind.CrossOver(self.data.close(0), self.L_line)

    def next(self):
        if self.order:
            return
        # 入场：价格突破上轨线且空仓时
        if self.buy_signal > 0 and self.buy_count == 0:
            self.buy_size = self.broker.getcash() * self.p.CASH_rate / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.p.stake = self.buy_size
            self.buy_count = 1
            self.order = self.buy()
        # 加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] and 0 < self.buy_count <= 4:
            self.buy_size = self.broker.getcash() * self.p.CASH_rate / self.ATR
            self.buy_size = int(self.buy_size / 100) * 100
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            self.buy_count += 1
        # 离场：价格跌破下轨线且持仓时
        elif self.sell_signal < 0 and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0
        # 止损：价格跌破买入价的2个ATR且持仓时
        elif self.data.close < (self.buyprice - self.p.ATR_period * self.ATR[0]) and self.buy_count > 0:
            self.order = self.sell()
            self.buy_count = 0

    # 交易记录日志（默认不打印结果）
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},成本:{order.executed.value},手续费:{order.executed.comm}，数量：{order.executed.size}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},成本: {order.executed.value},手续费{order.executed.comm}')

            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')


    def stop(self):
        self.log(f'(组合线：{self.p.long_period},{self.p.short_period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)