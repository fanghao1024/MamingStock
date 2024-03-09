import sys

sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_market_from_mysql
import printAnalyzers

get_daily_market_from_mysql.get_daily_market_qfq()

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


class LongShortStrategy(bt.Strategy):
	'''This strategy buys/sells upong the close price crossing
    upwards/downwards a Simple Moving Average.

    It can be a long-only strategy by setting the param "onlylong" to True
    '''
	params = dict(
		period=15,
		#stake=1,
		printout=False,
		onlylong=True,
		csvcross=False,
	)

	def start(self):
		pass

	def stop(self):
		pass

	def log(self, txt, dt=None):
		if self.p.printout:
			dt = dt or self.data.datetime[0]
			dt = bt.num2date(dt)
			print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		# To control operation entries
		self.orderid = None
		# Create SMA on 2nd data
		# sma = btind.MovAv.SMA(self.data, period=self.p.period)
		sma = btind.MovingAverageSimple(self.data.close, period=self.p.period)
		# Create a CrossOver Signal from close an moving average
		self.signal = btind.CrossOver(self.data.close, sma)
		self.signal.csv = self.p.csvcross

	def next(self):
		if self.orderid:
			return  # if an order is active, no new orders are allowed

		if self.signal > 0.0:  # cross upwards
			if self.position:
				self.log('CLOSE SHORT , %.2f' % self.data.close[0])

				self.close()

			self.log('BUY CREATE , %.2f' % self.data.close[0])
			self.buy()
			#self.buy(size=self.p.stake)

		elif self.signal < 0.0:
			if self.position:
				self.log('CLOSE LONG , %.2f' % self.data.close[0])
				self.close()

			if not self.p.onlylong:
				self.log('SELL CREATE , %.2f' % self.data.close[0])
				self.sell()
				#self.sell(size=self.p.stake)

	def notify_order(self, order):
		if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
			return  # Await further notifications

		if order.status == order.Completed:
			if order.isbuy():
				buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
				self.log(buytxt, order.executed.dt)
			else:
				selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
				self.log(selltxt, order.executed.dt)

		elif order.status in [order.Expired, order.Canceled, order.Margin]:
			self.log('%s ,' % order.Status[order.status])
			pass  # Simply log

		# Allow new orders
		self.orderid = None

	def notify_trade(self, trade):
		if trade.isclosed:
			self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
					 (trade.pnl, trade.pnlcomm))

		elif trade.justopened:
			self.log('TRADE OPENED, SIZE %2d' % trade.size)

	def notify(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enougth cash
		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				print(self.datas[0].datetime.date(0))
				print(f"已经买入.价格为{order.executed.price}\n市值：{order.executed.value}\n佣金:{order.executed.comm}")

				self.buyprice = order.executed.price
				self.buycomm = order.executed.comm
				self.opsize = order.executed.size
			else:  # Sell
				print(self.datas[0].datetime.date(0))
				print(f"已经卖出.价格为{order.executed.price}\n费用：{order.executed.value}\n佣金:{order.executed.comm}\n")

				gross_pnl = (order.executed.price - self.buyprice) * self.opsize

				net_pnl = gross_pnl - self.buycomm - order.executed.comm
				print('OPERATION PROFIT, GROSS %.2f, NET %.2f' %  (gross_pnl, net_pnl))

def runstrategy():
	args = parse_args()

	# Create a cerebro
	cerebro = bt.Cerebro()

	# Get the dates from the args
	fromdate = datetime.datetime.strptime(args.fromdate, '%Y%m%d')
	todate = datetime.datetime.strptime(args.todate, '%Y%m%d')

	# Create the 1st data
	# stock_daily_info=get_daily_market_from_mysql.get_daily_market_qfq('600519','20000101','20210416')
	stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('000625', '20100101', '20210416')
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
	cerebro.addstrategy(LongShortStrategy,
						period=args.period,
						onlylong=True,
						#csvcross=args.csvcross,
						#stake=args.stake
						)

	cerebro.addsizer(bt.sizers.PercentSizerInt, percents=20)
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
	cerebro.addanalyzer(GrossLeverage, _name='_grossLeverage')
	cerebro.addanalyzer(PositionsValue, _name='_positionsValue')
	cerebro.addanalyzer(PyFolio, _name='_pyFolio')
	cerebro.addanalyzer(LogReturnsRolling, _name='_logReturnsRolling')
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
	print('_grossLeverage:\n', printAnalyzers.get_GrossLeverageRatio(result.analyzers._grossLeverage.get_analysis()))
	print('_positionsValue:\n', printAnalyzers.get_PositionValue(result.analyzers._positionsValue.get_analysis()))
	print('_pyFolio:\n', printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[0], '\n',
		  printAnalyzers.get_PyFolio(result.analyzers._pyFolio.get_analysis())[1])
	print('_logReturnsRolling:\n',
		  printAnalyzers.get_LogReturnRolling(result.analyzers._logReturnsRolling.get_analysis()))
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

	parser.add_argument('--cash', default=100000, type=int,
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
