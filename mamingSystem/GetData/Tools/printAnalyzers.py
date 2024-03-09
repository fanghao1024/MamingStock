import pandas as pd
from collections import OrderedDict
'''
get_annualReturn(annualReturn)
功能：返回年收益率
接收参数：
cerebro.addanalyzer(AnnualReturn,_name='_annualReturn')
result.analyzers._annualReturn.get_analysis()

返回参数：
pd.DataFrame(columns=['year','return'])
        return
year          
2018  0.000458
2019 -0.018071
2020 -0.062472
2021 -0.028019
'''

def get_AnnualReturn(annualReturn):
	Return=pd.DataFrame()
	for i,j in annualReturn.items():
		Return=Return.append({'year':str(i),'return':j},ignore_index=True)

	Return.set_index(['year'], inplace=True)
	return Return

'''
get_sharpeRatio(sharpeRatio)
功能：返回夏普比率
接收参数：
cerebro.addanalyzer(SharpeRatio, legacyannual=True,_name='_sharpeRatio')
result.analyzers._sharpeRatio.get_analysis()

返回：
夏普比率
'''
def get_SharpeRatio(sharpeRatio):
	return sharpeRatio['sharperatio']

'''
get_timeReturn(timeReturn)
功能：返回设定时间节点的收益率
接收参数：
cerebro.addanalyzer(TimeReturn, timeframe=tframes[args.tframe],_name='_timeReturn')
choices=['days', 'weeks', 'months', 'years']
result.analyzers._timeReturn.get_analysis()

返回参数：
pd.DataFrame(columns=['datetime','return'])

_timeReturn:
               return
datetime            
2016-12-31  0.165846
2017-12-31 -0.019806
2018-12-31  0.000458
2019-12-31 -0.018071
2020-12-31 -0.062472
2021-12-31 -0.028019
'''
def get_TimeReturn(timeReturn):
	Return = pd.DataFrame()
	for i, j in timeReturn.items():
		Return = Return.append({'datetime': str(i), 'return': j}, ignore_index=True)

	Return.set_index(['datetime'], inplace=True)
	return Return

'''
_drawDown:
                        data
xiangmu                    
len              274.000000
drawdown          20.209971
moneydown      33688.000000
max_len         1047.000000
max_drawdown      21.407403
max_moneydown  35684.000000
'''
def get_DrawDown(draw_Down):
	drawDown=pd.DataFrame()
	drawDown['xiangmu']=['len','drawdown','moneydown','max_len','max_drawdown','max_moneydown']
	drawDown['data']=[draw_Down['len'],draw_Down['drawdown'],draw_Down['moneydown'],draw_Down['max']['len'],draw_Down['max']['drawdown'],draw_Down['max']['moneydown']]
	drawDown.set_index(['xiangmu'],inplace=True)
	return drawDown

def get_TradeAnalyzer(trade_analyzer):
	trade_dict_1 = OrderedDict()
	trade_dict_2 = OrderedDict()
	trade_info = trade_analyzer.copy()
	total_trade_num = trade_info['total']['total']
	total_trade_opened = trade_info['total']['open']
	total_trade_closed = trade_info['total']['closed']
	total_trade_len = trade_info['len']['total']
	long_trade_len = trade_info['len']['long']['total']
	short_trade_len = trade_info['len']['short']['total']

	longest_win_num = trade_info['streak']['won']['longest']
	longest_lost_num = trade_info['streak']['lost']['longest']
	net_total_pnl = trade_info['pnl']['net']['total']
	net_average_pnl = trade_info['pnl']['net']['average']
	win_num = trade_info['won']['total']
	win_total_pnl = trade_info['won']['pnl']['total']
	win_average_pnl = trade_info['won']['pnl']['average']
	win_max_pnl = trade_info['won']['pnl']['max']
	lost_num = trade_info['lost']['total']
	lost_total_pnl = trade_info['lost']['pnl']['total']
	lost_average_pnl = trade_info['lost']['pnl']['average']
	lost_max_pnl = trade_info['lost']['pnl']['max']

	trade_dict_1['total_trade_num'] = total_trade_num
	trade_dict_1['total_trade_opened'] = total_trade_opened
	trade_dict_1['total_trade_closed'] = total_trade_closed
	trade_dict_1['total_trade_len'] = total_trade_len
	trade_dict_1['long_trade_len'] = long_trade_len
	trade_dict_1['short_trade_len'] = short_trade_len
	trade_dict_1['longest_win_num'] = longest_win_num
	trade_dict_1['longest_lost_num'] = longest_lost_num
	trade_dict_1['net_total_pnl'] = net_total_pnl
	trade_dict_1['net_average_pnl'] = net_average_pnl
	trade_dict_1['win_num'] = win_num
	trade_dict_1['win_total_pnl'] = win_total_pnl
	trade_dict_1['win_average_pnl'] = win_average_pnl
	trade_dict_1['win_max_pnl'] = win_max_pnl
	trade_dict_1['lost_num'] = lost_num
	trade_dict_1['lost_total_pnl'] = lost_total_pnl
	trade_dict_1['lost_average_pnl'] = lost_average_pnl
	trade_dict_1['lost_max_pnl'] = lost_max_pnl

	long_num = trade_info['long']['total']
	long_win_num = trade_info['long']['won']
	long_lost_num = trade_info['long']['lost']
	long_total_pnl = trade_info['long']['pnl']['total']
	long_average_pnl = trade_info['long']['pnl']['average']
	long_win_total_pnl = trade_info['long']['pnl']['won']['total']
	long_win_max_pnl = trade_info['long']['pnl']['won']['max']
	long_lost_total_pnl = trade_info['long']['pnl']['lost']['total']
	long_lost_max_pnl = trade_info['long']['pnl']['lost']['max']

	short_num = trade_info['short']['total']
	short_win_num = trade_info['short']['won']
	short_lost_num = trade_info['short']['lost']
	short_total_pnl = trade_info['short']['pnl']['total']
	short_average_pnl = trade_info['short']['pnl']['average']
	short_win_total_pnl = trade_info['short']['pnl']['won']['total']
	short_win_max_pnl = trade_info['short']['pnl']['won']['max']
	short_lost_total_pnl = trade_info['short']['pnl']['lost']['total']
	short_lost_max_pnl = trade_info['short']['pnl']['lost']['max']

	trade_dict_2['long_num'] = long_num
	trade_dict_2['long_win_num'] = long_win_num
	trade_dict_2['long_lost_num'] = long_lost_num
	trade_dict_2['long_total_pnl'] = long_total_pnl
	trade_dict_2['long_average_pnl'] = long_average_pnl
	trade_dict_2['long_win_total_pnl'] = long_win_total_pnl
	trade_dict_2['long_win_max_pnl'] = long_win_max_pnl
	trade_dict_2['long_lost_total_pnl'] = long_lost_total_pnl
	trade_dict_2['long_lost_max_pnl'] = long_lost_max_pnl
	trade_dict_2['short_num'] = short_num
	trade_dict_2['short_win_num'] = short_win_num
	trade_dict_2['short_lost_num'] = short_lost_num
	trade_dict_2['short_total_pnl'] = short_total_pnl
	trade_dict_2['short_average_pnl'] = short_average_pnl
	trade_dict_2['short_win_total_pnl'] = short_win_total_pnl
	trade_dict_2['short_win_max_pnl'] = short_win_max_pnl
	trade_dict_2['short_lost_total_pnl'] = short_lost_total_pnl
	trade_dict_2['short_lost_max_pnl'] = short_lost_max_pnl

	trader_indicator = pd.DataFrame([trade_dict_1]).T
	trader_indicator.columns = ['普通交易指标值']
	long_short_indicator = pd.DataFrame([trade_dict_2]).T
	long_short_indicator.columns = ['多空交易指标值']
	return trader_indicator,long_short_indicator

def get_Carmar(_carmar):
	carmar = pd.DataFrame()
	for i, j in _carmar.items():
		carmar = carmar.append({'datetime': str(i), 'return': j}, ignore_index=True)

	carmar.set_index(['datetime'], inplace=True)
	return carmar

def get_TimeDrawDown(_timedrawdown):
	TimeDrawDown = pd.DataFrame()
	TimeDrawDown['xiangmu'] = ['maxdrawdown', 'maxdrawdownperiod']
	TimeDrawDown['data'] = [_timedrawdown['maxdrawdown'],_timedrawdown['maxdrawdownperiod']]
	TimeDrawDown.set_index(['xiangmu'], inplace=True)
	return TimeDrawDown

def get_GrossLeverageRatio(_grossleverageratio):
	GrossLeverageRatio = pd.DataFrame.from_dict(_grossleverageratio,orient='index',columns=['ratio'])
	return GrossLeverageRatio

'''
计算时间点的持仓价值
'''
def get_PositionValue(_positionvalue):
	PositionValue = pd.DataFrame.from_dict(_positionvalue,orient='index',columns=['value'])
	PositionValue.rename({0:'value'},inplace=True)
	return PositionValue

def get_PyFolio(_pyfolio):
	#PyFolio_return=pd.DataFrame.from_dict(_pyfolio['returns','gross_lev','positions'],orient='index',columns=['TimeReturn','PositionValue','Transactions','GrossLeverage'])
	PyFolio_return=pd.DataFrame.from_dict(_pyfolio['returns'],orient='index',columns=['TimeReturn'])

	PyFolio_grossLev=pd.DataFrame.from_dict(_pyfolio['gross_lev'],orient='index',columns=['GrossLeverage'])

	#print(_pyfolio['positions'])
	PyFolio_positionsValue = pd.DataFrame.from_dict(_pyfolio['positions'], orient='index',columns=['positionsValue','cash'])
	PyFolio_positionsValue.drop(PyFolio_positionsValue[PyFolio_positionsValue.cash=='cash'].index,inplace=True)

	PyFolio_transactions = pd.DataFrame.from_dict(_pyfolio['transactions'], orient='index', columns=['Transactions'])

	PyFolio_transactions.drop(PyFolio_transactions[PyFolio_transactions.index=='date'].index,inplace=True)

	PyFolio_transactions['amount'] = PyFolio_transactions['Transactions'].apply(lambda x: x[0])
	PyFolio_transactions['price'] = PyFolio_transactions['Transactions'].apply(lambda x: x[1])
	PyFolio_transactions['sid'] = PyFolio_transactions['Transactions'].apply(lambda x: x[2])
	PyFolio_transactions['symbol'] = PyFolio_transactions['Transactions'].apply(lambda x: x[3] if x[3]!='' else None)
	PyFolio_transactions['value'] = PyFolio_transactions['Transactions'].apply(lambda x: x[4])
	PyFolio_transactions.drop(['Transactions'],axis=1,inplace=True)


	PyFolio_Return_GrossLev_PositionsValue=pd.merge(PyFolio_return,PyFolio_grossLev,how='outer',left_index=True,right_index=True)
	PyFolio_Return_GrossLev_PositionsValue=pd.merge(PyFolio_Return_GrossLev_PositionsValue,PyFolio_positionsValue,how='outer',left_index=True,right_index=True)
	return PyFolio_Return_GrossLev_PositionsValue,PyFolio_transactions

'''
滚动的对数收益率
'''
def get_LogReturnRolling(_logreturnrolling):
	LogReturnRolling = pd.DataFrame.from_dict(_logreturnrolling, orient='index', columns=['logReturn'])
	return LogReturnRolling

def get_PeriodStats(_periodstats):
	PeriodStats=pd.DataFrame.from_dict(_periodstats,orient='index',columns=['value'])
	return PeriodStats

'''
rtot: Total compound return
ravg: Average return for the entire period (timeframe specific)
rnorm: Annualized/Normalized return
rnorm100: Annualized/Normalized return expressed in 100%
'''
def get_Returns(_returns):
	Returns=pd.DataFrame.from_dict(_returns,orient='index',columns=['rate'])
	return Returns

def get_SharpeRatio_A(_sharperatio_a):
	return _sharperatio_a['sharperatio']

def get_Transactions(_transactions):
	Transactions=pd.DataFrame.from_dict(_transactions,orient='index',columns=['Transactions'])
	Transactions['amount'] = Transactions['Transactions'].apply(lambda x: x[0])
	Transactions['price'] = Transactions['Transactions'].apply(lambda x: x[1])
	Transactions['sid'] = Transactions['Transactions'].apply(lambda x: x[2])
	Transactions['symbol'] = Transactions['Transactions'].apply(lambda x: x[3] if x[3] != '' else None)
	Transactions['value'] = Transactions['Transactions'].apply(lambda x: x[4])
	Transactions.drop(['Transactions'], axis=1, inplace=True)
	return Transactions

def get_VWR(_vwr):
	return _vwr['vwr']

'''
1.6 - 1.9 Below average
2.0 - 2.4 Average
2.5 - 2.9 Good
3.0 - 5.0 Excellent
5.1 - 6.9 Superb
7.0 - Holy Grail?
'''
def get_SQN(_sqn):
	SQN = pd.DataFrame.from_dict(_sqn, orient='index', columns=['value'])
	return SQN