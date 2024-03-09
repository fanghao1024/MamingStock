import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import akshare as ak
import talib as ta
import gc

# plt.switch_backend('cairo')

pd.set_option('display.max_columns', 500)

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

weekly_period = 26
fastperiod = 12
slowperiod = 26
signalperiod = 9


def fun_none():
	print('wrong type')
	return None


def transferToWeeklyLine(data, types):
	period_type = 'W'
	period_stock_data = data.resample(period_type).last()
	period_stock_data['open'] = data['open'].resample(period_type).first()
	period_stock_data['high'] = data['high'].resample(period_type).max()
	period_stock_data['low'] = data['low'].resample(period_type).min()
	period_stock_data['volume'] = data['volume'].resample(period_type).sum()
	if types == 'stock':
		period_stock_data['deal'] = data['deal'].resample(period_type).sum()
	elif types == 'index' or types == 'board':
		period_stock_data['amount'] = data['amount'].resample(period_type).sum()
	'''
	period_stock_data['zhenfu']=(period_stock_data['high']-period_stock_data['low'])/period_stock_data['close']
	period_stock_data['zhangdiefu']=(period_stock_data['close']-period_stock_data['open'])/period_stock_data['open']
	period_stock_data['zhangdiee']=period_stock_data['close']-period_stock_data['open']
	period_stock_data['turnover']=data['turnover'].resample(period_type).sum()
	'''

	period_stock_data = period_stock_data[period_stock_data['close'].notnull()]
	return period_stock_data


def PlotWeeklyLine(code, types, startday, endday):
	A = func_dist.get(types, fun_none)(code, startday, endday)
	A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)
	A = transferToWeeklyLine(A, types)
	ema_line = ta.EMA(A['close'], weekly_period)
	vol_sma = ta.SMA(A['volume'], 5)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	apds = [
		mpf.make_addplot(ema_line, type='line'),
		mpf.make_addplot(vol_sma, type='line', panel=1, color='black'),
		mpf.make_addplot(macd, type='line', panel=2, color='black',ylabel='macd\n'+str(fastperiod)+'-'+str(slowperiod)+'-'+str(signalperiod)),
		mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
		mpf.make_addplot(macdhist, type='bar', panel=2),
	]
	fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
						   volume=True, panel_ratios=(3, 1, 1), figscale=2, axtitle=types + code+' weekly',
						   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
	ax1 = axlist[0]
	ax1.set_yscale('log')
	plt.rcParams['axes.unicode_minus'] = False
	plt.show()


def PlotWeeklyLine_Save(code, types, startday, endday):
	filename = '../../stockdata/Week/' + types + '/' + types + code + '.png'
	A = func_dist.get(types, fun_none)(code, startday, endday)
	if A is None:
		return
	A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
	A.rename(columns={'trade_date': 'datetime'}, inplace=True)
	A['datetime'] = pd.to_datetime(A['datetime'])
	A.set_index(['datetime'], inplace=True)
	A = transferToWeeklyLine(A, types)
	ema_line = ta.EMA(A['close'], weekly_period)
	vol_sma = ta.SMA(A['volume'], 5)
	macd, macdsignal, macdhist = ta.MACD(A['close'], fastperiod, slowperiod, signalperiod)
	try:
		apds = [
			mpf.make_addplot(ema_line, type='line'),
			mpf.make_addplot(vol_sma, type='line', panel=1, color='black'),
			mpf.make_addplot(macd, type='line', panel=2, color='black',ylabel='macd\n'+str(fastperiod)+'-'+str(slowperiod)+'-'+str(signalperiod)),
			mpf.make_addplot(macdsignal, type='line', panel=2, color='red'),
			mpf.make_addplot(macdhist, type='bar', panel=2),
		]
		fig, axlist = mpf.plot(A, type='candle', addplot=apds, style=CN,
							   volume=True, panel_ratios=(3, 1, 1), figscale=2, axtitle=types + code+' weekly',
							   scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3}, returnfig=True)
		ax1 = axlist[0]
		ax1.set_yscale('log')
		plt.rcParams['savefig.dpi'] = 300
		plt.rcParams['axes.unicode_minus'] = False
		plt.savefig(filename)
		plt.clf()
		plt.close('all')
	except Exception as ee:
		print(filename, 'is wrong:', ee)
	finally:
		del A,ema_line,vol_sma,macd,macdsignal,macdhist
		gc.collect()


# plt.show()


def PlotWeekly_SaveAllIndex(startday, endday):
	stock_info_a_code_name_df = pd.read_excel('../data/index_code.xlsx', converters={u'code': str})
	mark = False
	types = 'index'
	lens = 10
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code, name)


# if mark == False and str(code) != '399422':
#	continue
# else:
#	mark = True
# PlotWeeklyLine_Save(code, types, startday, endday)


def PlotWeekly_SaveAllETF(startday, endday):
	mark = False
	types = 'ETF'
	ETF_category = ak.fund_etf_category_sina()
	lens = 10
	for code, name in zip(ETF_category.iloc[:, 0], ETF_category.iloc[:, 1]):
		print(code, name)
		# if mark == False and str(code) != '300391':
		#   continue
		# else:
		#   mark = True
		PlotWeeklyLine_Save(code, types, startday, endday)


def PlotWeekly_SaveAllBoard(startday, endday):
	mark = False
	types = 'board'

	stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

	for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
		print(code, name)
		# if mark == False and str(code) != '300391':
		#   continue
		# else:
		#   mark = True
		PlotWeeklyLine_Save(code, types, startday, endday)


def PlotWeekly_SaveAllStock(startday, endday):
	types = 'stock'

	stock_info_a_code_name_df = ak.stock_info_a_code_name()

	mark = False
	lens = 10
	for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
		print(code, name)
		#if mark == False and str(code) != '600368':
		#	continue
		#else:
		#	mark = True

		PlotWeeklyLine_Save(code, types, startday, endday)


# PlotWeekly_SaveAllBoard('20100101','20220218')
# PlotWeekly_SaveAllIndex('20170101', '20220218')
#PlotWeekly_SaveAllStock('20100101', '20220218')
# PlotWeekly_SaveAllETF('20100101','20220218')
# PlotWeeklyLine_Save('399006', 'index', '20180101', '20220218')

PlotWeeklyLine('516910','ETF','20180101','20220221')
