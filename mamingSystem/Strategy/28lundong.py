import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_ETF_daily_market_from_mysql
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

class TwoEightStrategy(bt.Strategy):
	# 默认参数
	params = (('period', 20),
			  ('printlog', True),
			  ('CASH_rate',0.8),
			  )

	def __init__(self):

		self.order = None
		self.buyprice = 0
		self.buycomm = 0
		self.buy_size = 0
		self.buy_count = 0
		self.last_buy_cash=0

		self.sma50s=bt.indicators.SMA(self.data.close,period=self.p.period)
		self.sma300s=bt.indicators.SMA(self.data1.close,period=self.p.period)
		self.sma500s = bt.indicators.SMA(self.data2.close, period=self.p.period)


	def next(self):
		if self.order:
			return


		self.sma50=(self.datas[0].close[0]-self.datas[0].close[-self.p.period])/self.datas[0].close[-self.p.period]
		self.sma300 = (self.datas[1].close[0] - self.datas[1].close[-self.p.period]) / self.datas[1].close[-self.p.period]
		self.sma500 = (self.datas[2].close[0] - self.datas[2].close[-self.p.period]) / self.datas[2].close[-self.p.period]

		self.sma50_hold=self.getposition(self.datas[0]).size
		self.sma300_hold = self.getposition(self.datas[1]).size
		self.sma500_hold = self.getposition(self.datas[2]).size

		if self.sma50_hold>0 or self.sma300_hold>0 or self.sma500_hold>0:

			if self.sma50 <= 0 and self.sma50_hold > 0 :
				self.close(self.datas[0])

			if self.sma300 <= 0 and self.sma300_hold > 0:
				self.close(self.datas[1])

			if self.sma500 <= 0 and self.sma500_hold > 0:
				self.close(self.datas[2])

		elif self.sma50-self.sma300>0.01 \
				and self.sma50-self.sma500>0.01 \
				and self.sma50>0 \
				and (self.sma50_hold<0.1 and self.sma300_hold<0.1 and self.sma500_hold<0.1):

			self.buy_size= self.broker.getcash() * self.p.CASH_rate / self.datas[0].close[0]
			self.buy_size= int(self.buy_size / 100) * 100
			print()
			self.buy(data=self.datas[0], size=self.buy_size)


		elif self.sma300 - self.sma50 > 0.01 \
				and self.sma300 - self.sma500 > 0.01 \
				and self.sma300 > 0 \
				and (self.sma50_hold < 0.1 and self.sma300_hold < 0.1 and self.sma500_hold < 0.1):
			self.buy_size = self.broker.getcash() * self.p.CASH_rate / self.datas[1].close[0]
			self.buy_size = int(self.buy_size / 100) * 100
			self.buy(data=self.datas[1], size=self.buy_size)

		elif self.sma500 - self.sma300 > 0.01 \
				and self.sma500 - self.sma50 > 0.01 \
				and self.sma500 > 0 \
				and (self.sma50_hold < 0.1 and self.sma300_hold < 0.1 and self.sma500_hold < 0.1):
			self.buy_size = self.broker.getcash() * self.p.CASH_rate / self.datas[2].close[0]
			self.buy_size = int(self.buy_size / 100) * 100
			self.buy(data=self.datas[2], size=self.buy_size)


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
		self.log(f'(组合线：{self.p.period})；期末总资金: {self.broker.getvalue():.2f}', doprint=True)


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
	lines = ('datetime', 'ETF_code', 'open', 'high','low','close','volume')
	# datetime (always 1st) and then the desired order for
	params = (
		('datetime', None),  # inherited from parent class
		('ETF_code', -1),  # default field pos 1
		('open', -1),  # default field pos 2
		('high', -1),
		('low' , -1),
		('close',-1),
		('volume',-1),

	)

def getETFData(ETF_code,startday,endday):
	etf_daily_info = get_ETF_daily_market_from_mysql.get_ETF_daily_market_information(ETF_code, startday,endday)
	# etf_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('601633', '20100101', '20210416')

	# date  ETF_code   ETF_name   open   high    low  close    volume
	etf_daily_info['date'] = etf_daily_info['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	etf_daily_info['ETF_code'] = etf_daily_info['ETF_code'].apply(lambda x: x[2:]).astype(float)
	etf_daily_info['open'] = etf_daily_info['open'].astype(float)
	etf_daily_info['high'] = etf_daily_info['high'].astype(float)
	etf_daily_info['low'] = etf_daily_info['low'].astype(float)
	etf_daily_info['close'] = etf_daily_info['close'].astype(float)
	etf_daily_info['volume'] = etf_daily_info['volume'].astype(float)
	# etf_daily_info['日增长率'] = etf_daily_info['日增长率'].astype(float)
	order = ['date', 'ETF_code', 'open', 'high', 'low', 'close', 'volume']
	etf_daily_info = etf_daily_info[order]
	etf_daily_info.rename(columns={'date': 'datetime'}, inplace=True)
	etf_daily_info['datetime'] = pd.to_datetime(etf_daily_info['datetime'])
	etf_daily_info.set_index(['datetime'], inplace=True)

	print(etf_daily_info)
	data = Stock_data(dataname=etf_daily_info, nocase=True, )
	return data

def runstrategy():
	args = parse_args()

	# Create a cerebro
	cerebro = bt.Cerebro()

	# Get the dates from the args
	fromdate = datetime.datetime.strptime(args.fromdate, '%Y%m%d')
	todate = datetime.datetime.strptime(args.todate, '%Y%m%d')

	data0=getETFData('sh510050', '20170101', '20211015')
	# data = bt.feeds.PandasData(dataname=etf_daily_info,nocase=True,)

	# Add the 1st data to cerebro
	cerebro.adddata(data0,name='sz50')

	data1=getETFData('sh510300','20170101', '20211015')
	cerebro.adddata(data1,name='hs300')

	data2 = getETFData('sh510500', '20170101', '20211015')
	cerebro.adddata(data2,name='zz500')

	# Add the strategy
	'''
	cerebro.addstrategy(AberrationStrategy,
						period=args.period,
						onlylong=True,
						#csvcross=args.csvcross,
						#stake=args.stake
						)
	'''

	cerebro.addstrategy(TwoEightStrategy)
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
	trader_indicator, long_short_indicator = printAnalyzers.get_TradeAnalyzer(
		result.analyzers._tradeAnalyzer.get_analysis())
	print('_tradeAnalyzer:\n', trader_indicator, '\n', long_short_indicator)
	print('_calmar:\n', printAnalyzers.get_Carmar(result.analyzers._calmar.get_analysis()))
	print('_timedrawdown:\n', printAnalyzers.get_TimeDrawDown(result.analyzers._timeDrawDown.get_analysis()))
	#print('_grossLeverage:\n', printAnalyzers.get_GrossLeverageRatio(result.analyzers._grossLeverage.get_analysis()))
	#print('_positionsValue:\n', printAnalyzers.get_PositionValue(result.analyzers._positionsValue.get_analysis()))
	#print('_pyFolio:\n', printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[0], '\n',printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[1])
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