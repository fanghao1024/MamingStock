import sys,os
os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')
import get_daily_upanddown_from_mysql
import pandas as pd
import numpy as np
import talib as ta

def TengLuoFactor(index_name='AllA',startday='19000101',endday='21001231'):
	df=get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name,startday,endday)
	df['tengluo']=df['up']-df['down']
	df['tengluosum']=df['tengluo'].cumsum()
	return df[['trade_date','tengluosum']]

def TengLuoFactor_shang(index_name='AllA',startday='19000101',endday='21001231'):
	df=get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name,startday,endday)
	df['tengluo']=df['up']/df['down']
	return df[['trade_date','tengluo']]

#sqrt(up/flat-down/flat)
def TengLuoFactor_Bolton(index_name='AllA',startday='19000101',endday='21001231'):
	df = get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name, startday, endday)
	df['flat'].loc[df['flat']==0]=0.5
	df['tengluo'] = (df['up'] - df['down'])/df['flat']
	df['tengluo'].loc[df['tengluo'] > 0] = np.sqrt(df['tengluo'].loc[df['tengluo']>0])
	df['tengluo'].loc[df['tengluo'] < 0] = -np.sqrt(df['tengluo'].loc[df['tengluo'] < 0]*(-1))
	df['Bolton']=df['tengluo'].cumsum()
	return df[['trade_date','Bolton']]

#麦克里伦摆荡指标，分别周期长度为19和39EMA的腾落差值
#麦克里伦摆荡指标=【（up-down）的19天EMA】-【（up-down）的39天EMA】
def McClellanOscillator(index_name='AllA',startday='19000101',endday='21001231',shortTime=19,longTime=39):
	df = get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name, startday, endday)
	df['tengluo'] = df['up'] - df['down']
	df['McClellan']=ta.EMA(df['tengluo'],shortTime)-ta.EMA(df['tengluo'],longTime)
	df = df[df[str('McClellan')].notnull()]
	return df[['trade_date','McClellan']]


#麦克里伦摆荡加总指标，累加麦克里伦摆荡指标
def McClellanOscillator_cum(index_name='AllA',startday='19000101',endday='21001231',shortTime=19,longTime=39):
	df = get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name, startday, endday)
	df['tengluo'] = df['up'] - df['down']
	df['McClellan']=ta.EMA(df['tengluo'],shortTime)-ta.EMA(df['tengluo'],longTime)
	df = df[df[str('McClellan')].notnull()]
	df['McClellan']=df['McClellan'].cumsum()
	return df[['trade_date','McClellan']]

#阿姆斯（交易者指数）
#TRIN=(上涨家数/下跌家数)/(上涨成交量/下跌成交量)
#指标呈反向走势
def TRIN(index_name='AllA',startday='19000101',endday='21001231'):
	df = get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name, startday, endday)
	df['TRIN'] = (df['up'] / df['down'])/(df['up_amount']/df['down_amount'])
	return df[['trade_date','TRIN']]

def TRIN_reverse(index_name='AllA',startday='19000101',endday='21001231'):
	df = get_daily_upanddown_from_mysql.get_daily_upanddown_information(index_name, startday, endday)
	df['TRIN_reverse'] = (df['up_amount'] / df['down_amount'])/(df['up'] / df['down'])
	return df[['trade_date', 'TRIN_reverse']]

#print(TRIN_reverse('CYB','20200101','20220118'))