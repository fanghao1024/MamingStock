import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import akshare as ak
import talib as ta
import gc

# plt.switch_backend('cairo')
pd.set_option('display.max_columns', 500)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')

import get_daily_index_market_from_mysql
import get_daily_industry_market_from_mysql
import get_daily_market_from_mysql
import get_daily_ETF_market_from_mysql

func_dist = {'stock': get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf, \
			 'index': get_daily_index_market_from_mysql.get_daily_index_market_information, \
			 'board': get_daily_industry_market_from_mysql.get_daily_board_market_bfq_from_dfcf, \
			 'ETF': get_daily_ETF_market_from_mysql.get_ETF_daily_market_information}

cncolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
# Create a new style based on `nightclouds` but with my own `marketcolors`:
CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor, rc={'font.family': 'SimHei'})

Daily_period = 22
fastperiod = 12
slowperiod = 26
signalperiod = 9


def fun_none():
	print('wrong type')
	return None


def PlotDailyLine(code, types, startday, endday):
	A = func_dist.get(types, fun_none)(code, startday, endday)
	A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'trade_date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)

	ema_line = ta.EMA(A['close'], Daily_period)
	upperband, middleband, lowerband = ta.BBANDS(A['close'], timeperiod=Daily_period, nbdevup=2, nbdevdn=2, matype=0)
	vol_sma = ta.SMA(A['volume'], 5)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	qiangli_short_period=2
	qiangli_long_period=13
	qiangli_short = ta.EMA((A['close'] - A['close'].shift(-1)) * A['volume'], 2)
	qiangli_long = ta.EMA((A['close'] - A['close'].shift(-1)) * A['volume'], 13)
	elder_long = A['high'] - ema_line
	elder_short = A['low'] - ema_line

	apds = [
		# mpf.make_addplot(ema_line, type='line'),
		mpf.make_addplot(upperband, type='line'),
		mpf.make_addplot(middleband, type='line',ylabel='boll\n'+str(Daily_period)),
		mpf.make_addplot(lowerband, type='line'),
		mpf.make_addplot(vol_sma, type='line', panel=1, color='black'),
		mpf.make_addplot(macd, type='line', panel=2, color='black',ylabel='MACD\n' + str(fastperiod) + '-' + str(slowperiod) + '-' + str(signalperiod)),
		mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
		mpf.make_addplot(macdhist, type='bar', panel=2),
		mpf.make_addplot(qiangli_short, type='line', panel=3, color='red',ylabel='qiangli\n' + str(qiangli_short_period) + '-' + str(qiangli_long_period)),
		mpf.make_addplot(qiangli_long, type='line', panel=3, color='black'),
		mpf.make_addplot(elder_long, type='bar', panel=4, color='red', ylabel='elder_long'),
		mpf.make_addplot(elder_short, type='bar', panel=5, color='green', ylabel='elder_short'),
	]
	fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
						   volume=True, panel_ratios=(2, 1, 1, 1, 0.5, 0.5), figscale=2, axtitle=types + code+' daily',
						   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
	ax1 = axlist[0]
	ax1.set_yscale('log')
	plt.rcParams['axes.unicode_minus'] = False
	plt.show()


def PlotDailyLine_self(code, types, startday, endday):
	filename = '../../stockdata/daily/' + types + '/' + types + code + '_1.png'
	A = func_dist.get(types, fun_none)(code, startday, endday)
	if A is None:
		return
	A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'trade_date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)

	ema_line = ta.EMA(A['close'], Daily_period)
	atr = ta.ATR(A['high'], A['low'], A['close'], timeperiod=14)
	upperband, lowerband = ema_line + atr * 2.5, ema_line - atr * 2.5

	vol_sma = ta.SMA(A['volume'], 5)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	ROC_period = 10
	ROC = ta.ROC(A['close'], timeperiod=ROC_period)
	RSI_period = 10
	RSI = ta.RSI(A['close'], timeperiod=RSI_period)
	# slowk, slowd = ta.STOCH(A['high'], A['low'], A['close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,slowd_matype=0)
	try:
		apds = [
			# mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(upperband, type='line'),
			mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(lowerband, type='line'),
			mpf.make_addplot(vol_sma, type='line', panel=1, color='black'),
			mpf.make_addplot(macd, type='line', panel=2, color='black',
							 ylabel='MACD\n' + str(fastperiod) + '-' + str(slowperiod) + '-' + str(signalperiod)),
			mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
			mpf.make_addplot(macdhist, type='bar', panel=2),
			mpf.make_addplot(ROC, type='line', panel=3, color='red', ylabel='ROC\n' + str(ROC_period)),
			mpf.make_addplot(RSI, type='line', panel=4, color='black', ylabel='RSI\n' + str(RSI_period)),
			# mpf.make_addplot(slowk, type='line', panel=5, color='red'),
			# mpf.make_addplot(slowd, type='line', panel=5, color='green'),
		]
		fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
							   volume=True, panel_ratios=(1.5, 1, 1, 1, 1), figscale=2, axtitle=types + code,
							   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
		ax1 = axlist[0]
		ax1.set_yscale('log')
		plt.rcParams['savefig.dpi'] = 300
		plt.rcParams['axes.unicode_minus'] = False
		plt.show()
		plt.cla()
		plt.clf()
		plt.close('all')
	except Exception as ee:
		print(filename, 'is wrong:', ee)
	finally:
		del A, ema_line, atr, upperband, lowerband, vol_sma, macd, macdsignal, macdhist, ROC, RSI
		gc.collect()


def PlotDailyLine_Save(code, types, startday, endday):
	filename = '../../stockdata/daily/' + types + '/' + types + code + '.png'
	A = func_dist.get(types, fun_none)(code, startday, endday)
	if A is None:
		return
	A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'trade_date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)

	ema_line = ta.EMA(A['close'], Daily_period)
	upperband, middleband, lowerband = ta.BBANDS(A['close'], timeperiod=Daily_period, nbdevup=2, nbdevdn=2, matype=0)
	vol_sma_period = 5
	vol_sma = ta.SMA(A['volume'], vol_sma_period)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	qiangli_short_period = 2
	qiangli_long_period = 13
	qiangli_short = ta.EMA((A['close'] - A['close'].shift(-1)) * A['volume'], qiangli_short_period)
	qiangli_long = ta.EMA((A['close'] - A['close'].shift(-1)) * A['volume'], qiangli_long_period)
	elder_long = A['high'] - ema_line
	elder_short = A['low'] - ema_line
	try:
		apds = [
			# mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(upperband, type='line'),
			mpf.make_addplot(middleband, type='line'),
			mpf.make_addplot(lowerband, type='line'),
			mpf.make_addplot(vol_sma, type='line', panel=1, color='black', ylabel=str(vol_sma_period)),
			mpf.make_addplot(macd, type='line', panel=2, color='black',
							 ylabel='MACD\n' + str(fastperiod) + '-' + str(slowperiod) + '-' + str(signalperiod)),
			mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
			mpf.make_addplot(macdhist, type='bar', panel=2),
			mpf.make_addplot(qiangli_short, type='line', panel=3, color='red',
							 ylabel='qiangli\n' + str(qiangli_short_period) + '-' + str(qiangli_long_period)),
			mpf.make_addplot(qiangli_long, type='line', panel=3, color='black'),
			mpf.make_addplot(elder_long, type='bar', panel=4, color='red', ylabel='elder_long'),
			mpf.make_addplot(elder_short, type='bar', panel=5, color='green', ylabel='elder_short'),
		]
		fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
							   volume=True, panel_ratios=(2, 1, 1, 1, 0.5, 0.5), figscale=2, axtitle=types + code,
							   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
		ax1 = axlist[0]
		ax1.set_yscale('log')
		plt.rcParams['savefig.dpi'] = 300
		plt.rcParams['axes.unicode_minus'] = False
		plt.savefig(filename)
		plt.cla()
		plt.clf()
		plt.close('all')
	except Exception as ee:
		print(filename, 'is wrong:', ee)
	finally:
		del A, upperband, middleband, lowerband, vol_sma, macd, macdsignal, macdhist, qiangli_long, qiangli_short, elder_long, elder_short
		gc.collect()


# plt.show()

def PlotDailyLine_Save_self(code, types, startday, endday):
	filename = '../../stockdata/daily/' + types + '/' + types + code + '_1.png'
	A = func_dist.get(types, fun_none)(code, startday, endday)
	if A is None:
		return
	A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'trade_date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)

	ema_line = ta.EMA(A['close'], Daily_period)
	atr = ta.ATR(A['high'], A['low'], A['close'], timeperiod=14)
	upperband, lowerband = ema_line + atr * 2.5, ema_line - atr * 2.5

	vol_sma = ta.SMA(A['volume'], 5)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	ROC_period = 10
	ROC = ta.ROC(A['close'], timeperiod=ROC_period)
	RSI_period = 10
	RSI = ta.RSI(A['close'], timeperiod=RSI_period)
	# slowk, slowd = ta.STOCH(A['high'], A['low'], A['close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,slowd_matype=0)
	try:
		apds = [
			# mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(upperband, type='line'),
			mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(lowerband, type='line'),
			mpf.make_addplot(vol_sma, type='line', panel=1, color='black'),
			mpf.make_addplot(macd, type='line', panel=2, color='black',
							 ylabel='MACD\n' + str(fastperiod) + '-' + str(slowperiod) + '-' + str(signalperiod)),
			mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
			mpf.make_addplot(macdhist, type='bar', panel=2),
			mpf.make_addplot(ROC, type='line', panel=3, color='red', ylabel='ROC\n' + str(ROC_period)),
			mpf.make_addplot(RSI, type='line', panel=4, color='black', ylabel='RSI\n' + str(RSI_period)),
			# mpf.make_addplot(slowk, type='line', panel=5, color='red'),
			# mpf.make_addplot(slowd, type='line', panel=5, color='green'),
		]
		fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
							   volume=True, panel_ratios=(1.5, 1, 1, 1, 1), figscale=2, axtitle=types + code,
							   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
		ax1 = axlist[0]
		ax1.set_yscale('log')
		plt.rcParams['savefig.dpi'] = 300
		plt.rcParams['axes.unicode_minus'] = False
		plt.savefig(filename)
		plt.cla()
		plt.clf()
		plt.close('all')
	except Exception as ee:
		print(filename, 'is wrong:', ee)
	finally:
		del A, ema_line, atr, upperband, lowerband, vol_sma, macd, macdsignal, macdhist, ROC, RSI
		gc.collect()


def PlotDaily_SaveAllIndex(startday, endday):
	stock_info_a_code_name_df = pd.read_excel('../data/index_code.xlsx', converters={u'code': str})
	mark = False
	types = 'index'
	lens = 10
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code, name)
		PlotDailyLine_Save(code, types, startday, endday)
		PlotDailyLine_Save_self(code, types, startday, endday)


def PlotDaily_SaveAllETF(startday, endday):
	mark = False
	types = 'ETF'
	ETF_category = ak.fund_etf_category_sina()
	lens = 10
	for code, name in zip(ETF_category.iloc[:, 0], ETF_category.iloc[:, 1]):
		print(code, name)
		PlotDailyLine_Save(code, types, startday, endday)
		PlotDailyLine_Save_self(code, types, startday, endday)


def PlotDaily_SaveAllBoard(startday, endday):
	mark = False
	types = 'board'

	stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

	for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
		print(code, name)
		PlotDailyLine_Save(code, types, startday, endday)
		PlotDailyLine_Save_self(code, types, startday, endday)


def PlotDaily_SaveAllStock(startday, endday):
	types = 'stock'

	stock_info_a_code_name_df = ak.stock_info_a_code_name()

	mark = False

	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code, name)
		if mark == False and str(code) != '601880':
			continue
		else:
			mark = True

		PlotDailyLine_Save(code, types, startday, endday)
		PlotDailyLine_Save_self(code, types, startday, endday)


# PlotDaily_SaveAllBoard('20170101','20220217')
# PlotDaily_SaveAllIndex('20170101','20220217')
PlotDaily_SaveAllStock('20170101', '20220217')
#PlotDaily_SaveAllETF('20170101', '20220217')
# PlotDailyLine_Save_self('399006', 'index', '20190101', '20220218')

# PlotPnf('399006','index','20120101','20220127')
#PlotDailyLine('601588','stock','20190101','20220104')
#PlotDailyLine_self('601588','stock','20190101','20220104')
