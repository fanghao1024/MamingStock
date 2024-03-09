import akshare as ak
import re
import pandas as pd
import sys


def getTradeDate():
	tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
	tool_trade_date_hist_sina_df['trade_date'] = tool_trade_date_hist_sina_df['trade_date'].astype(str)
	tool_trade_date_hist_sina_df['trade_date'] = tool_trade_date_hist_sina_df['trade_date'].apply(lambda x: re.sub('-', '', x))
	return tool_trade_date_hist_sina_df

def getPeriodTradeDate(startday,endday):
	tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
	tool_trade_date_hist_sina_df['trade_date'] = tool_trade_date_hist_sina_df['trade_date'].astype(str)
	tool_trade_date_hist_sina_df['trade_date'] = tool_trade_date_hist_sina_df['trade_date'].apply(
		lambda x: re.sub('-', '', x))
	return tool_trade_date_hist_sina_df[(tool_trade_date_hist_sina_df['trade_date']>=startday) & (tool_trade_date_hist_sina_df['trade_date']<=endday)]

'''
传入:pandas.DataFrame startday endday 
startday默认为pandas.DataFrame的最早日期
endday默认为pandas.DataFrame的最晚日期
pandas.DataFrame格式：
           stock_code open high low  close volume  outstanding_share  turnover
datetime 

返回：
index为startday至endday的pandas.DataFrame

如pandas.DataFrame的最早最晚日期和startday与endday不一致：
若startday早于pandas.DataFrame的最早日期，则其之间的数据都与pandas.DataFrame最早日期的数据一致
若endday早于pandas.DataFrame的最晚日期，则pandas.DataFrame最晚日期后的数据都为0
若pandas.DataFrame内部日期因停牌等原因缺少交易日的，则补齐交易日，数据复制停牌前一天的数据
'''

def fillTradeDate(stockDataFrame,startday,endday):
	tradeSeries=pd.read_excel('../data/tradeCalendar.xlsx')
	df_startday = stockDataFrame.iloc[0][0]
	df_endday = stockDataFrame.iloc[-1][0]

	tradeSeries['trade_date']=tradeSeries['trade_date'].astype(str)
	tradeSeries=tradeSeries[(tradeSeries['trade_date']>=startday) & (tradeSeries['trade_date']<=endday)][['trade_date']]
	stocktemp =tradeSeries[(tradeSeries['trade_date']>=df_startday) & (tradeSeries['trade_date']<=df_endday)][['trade_date']].copy()
	tradeSeries.reset_index(inplace=True)
	tradeSeries.drop('index',axis=1,inplace=True)

	stocktemp=pd.merge(stocktemp,stockDataFrame,left_on='trade_date',right_on='trade_date',how='outer')
	stocktemp.fillna(method='ffill',inplace=True)


	if startday < df_startday:
		stocktemp1 = tradeSeries[tradeSeries['trade_date'] < df_startday][['trade_date']].copy()
		stocktemp = pd.merge(stocktemp,stocktemp1, left_on='trade_date', right_on='trade_date', how='outer')
		stocktemp=stocktemp.sort_values(by='trade_date')
		stocktemp['stock_code']=stocktemp['stock_code'].fillna(method='ffill')
		stocktemp['volume']=stocktemp['volume'].fillna(0)
		stocktemp.fillna(method='bfill',inplace=True)

	if endday > df_endday:
		stocktemp2 = tradeSeries[tradeSeries['trade_date'] >df_endday][['trade_date']].copy()
		stocktemp = pd.merge(stocktemp, stocktemp2, left_on='trade_date', right_on='trade_date', how='outer')
		stocktemp = stocktemp.sort_values(by='trade_date')
		stocktemp['stock_code']=stocktemp['stock_code'].fillna(method='ffill')
		stocktemp.fillna(0,inplace=True)

	return stocktemp
	

#print(getPeriodTradeDate('20210401','20210425'))
#stock_daily_info = get_daily_market_from_mysql.get_daily_market_qfq('600009', '20100101', '20210416')
#print(stock_daily_info)
#print(fillTradeDate(stock_daily_info,'20100101', '20210416'))