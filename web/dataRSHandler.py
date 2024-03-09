#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from tornado import gen
import web.base as webBase
import logging

# 首映 bokeh 画图。
from bokeh.plotting import figure
from bokeh.embed import components
import datetime
import libs.common as common
import stockstats
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import DatetimeTickFormatter, FreehandDrawTool, HoverTool, ColumnDataSource, CrosshairTool
import mamingSystem.GetData.FromMySQL.get_daily_market_from_mysql as get_daily_info
import mamingSystem.GetData.FromMySQL.get_daily_index_market_from_mysql as get_index_info
import mamingSystem.GetData.FromMySQL.get_daily_industry_market_from_mysql as get_board_info
import mamingSystem.GetData.FromMySQL.get_daily_ETF_market_from_mysql as get_etf_info
import talib

pd.set_option('display.max_columns', None)

line_Color = ['yellow', 'Fuchsia', 'Indigo', 'blue', 'OrangeRed', 'black']

# 获得页面数据。
class GetDataRSHandler(webBase.BaseHandler):
	@gen.coroutine
	def get(self):
		codes = self.get_argument("code", default=None, strip=False).split('_')
		print('codes:', codes)
		types = codes[0]
		code = codes[1]
		logging.info(code)
		# self.uri_ = ("self.request.url:", self.request.uri)
		# print self.uri_
		comp_list = []

		try:
			date_now = datetime.datetime.now()
			date_end = date_now.strftime("%Y-%m-%d")
			date_start = (date_now + datetime.timedelta(days=-1200)).strftime("%Y-%m-%d")
			print(code, date_start, date_end)

			# open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
			# 使用缓存方法。加快计算速度。

			startdate = ''.join(date_start.split('-'))
			enddate = ''.join(date_end.split('-'))
			if types == 'stock':
				stock = get_daily_info.get_daily_market_qfq_from_dfcf(code, startdate, enddate)
				stock.rename(columns={'deal': 'amount', 'zhenfu': 'amplitude', 'zhangdiefu': 'quote_change',
									  'zhangdiee': 'ups_downs'}, inplace=True)
			# stock = common.get_hist_data_cache(code, date_start, date_end)
			elif types == 'index':
				stock = get_index_info.get_daily_index_market_information(code, startdate, enddate)
			elif types == 'board':
				stock = get_board_info.get_daily_board_market_bfq_from_dfcf(code, startdate, enddate)
			elif types == 'etf':
				stock = get_etf_info.get_ETF_daily_market_information(code, startdate, enddate)
			stock1 = get_index_info.get_daily_index_market_information('000300', startdate, enddate)

			logging.info(stock.head(1))

			# print(stock) [186 rows x 14 columns]
			# 初始化统计类
			# stockStat = stockstats.StockDataFrame.retype(pd.read_csv("002032.csv"))
			stockStat = stockstats.StockDataFrame.retype(stock)
			stockStat1 = stockstats.StockDataFrame.retype(stock1)

			batch_add(comp_list, stockStat, stockStat1)


		except Exception as e:
			logging.info("error :", e)
		logging.info("#################### GetStockHtmlHandlerEnd ####################")

		self.render("stock_indicators.html", comp_list=comp_list,
					pythonStockVersion=common.__version__,
					leftMenu=webBase.GetLeftMenu(self.request.uri))

indicators_dic_myself = [
	{
		"title": "RS指标计算n天差",
		"desc": "可以计算，向前n天，和向后n天的差。",
		"mark": "RS",
		"dic": ["close", "close_-5_d", "close_-10_d", "close_-22_d"]
	}
]

# 批量添加数据。
def batch_add(comp_list, stockStat, stockStat1):

	for conf in indicators_dic_myself:
		# logging.info(conf)
		print('conf:', conf)
		comp_list.append(add_plot(stockStat, stockStat1, conf))


def plot_RSFactor(stockStat, stockStat1, conf):
	p_list = []
	print(stockStat)
	# 循环 多个line 信息。

	# stockStat.reset_index()
	stockStats = pd.DataFrame(stockStat.index)
	stockStats.reset_index(inplace=True)

	p1 = figure(width=1750, height=320, y_axis_type="log")

	renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
	draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
	p1.add_tools(draw_tool)
	p1.toolbar.active_drag = draw_tool

	inc = stockStat.close > stockStat.open
	dec = stockStat.open >= stockStat.close
	d={
		i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
	}
	p1.xaxis.major_label_overrides = d
	# p1.xaxis.bounds = (0, stockStat.index[-1])
	p1.x_range.range_padding = 0.02
	w = 0.5

	p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
	p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
			line_color="red")
	p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
			line_color="green")
	p_list.append([p1])

	# 沪深300指数显示
	p1 = figure(width=1750, height=320,  y_axis_type="log")

	renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
	draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
	p1.add_tools(draw_tool)
	p1.toolbar.active_drag = draw_tool

	inc = stockStat1.close > stockStat1.open
	dec = stockStat1.open >= stockStat1.close

	p1.xaxis.major_label_overrides = d
	# p1.xaxis.bounds = (0, stockStat.index[-1])
	p1.x_range.range_padding = 0.02
	w = 0.5

	print(len(stockStats.index),len(stockStat1.high),len(stockStat1.low))
	p1.segment(stockStats.index, stockStat1.high, stockStats.index, stockStat1.low, color="black")
	p1.vbar(stockStats.index[inc], w, stockStat1.open[inc], stockStat1.close[inc], fill_color="red",
			line_color="red")

	p1.vbar(stockStats.index[dec], w, stockStat1.open[dec], stockStat1.close[dec], fill_color="green",
			line_color="green")
	p1.x_range = p_list[0][0].x_range
	p_list.append([p1])

	#stock_RS=pd.DataFrame(stockStat.index)
	#stock_RS['date']=stockStat.index
	num1=pd.DataFrame(stockStat['close'])
	num2=pd.DataFrame(stockStat1['close'])
	num1.rename(columns={'close': 'A_close'}, inplace = True)
	num2.rename(columns={'close': 'B_close'}, inplace=True)

	stock_RS = pd.merge(num1, num2, left_index=True, right_index=True)
	print(stock_RS)
	stock_RS['rs'] = stock_RS['A_close'] / stock_RS['B_close']
	stock_RS.dropna(axis=0, how='all')

	stock_RS = stock_RS[['rs']]

	ROCPeriod = 10
	print('2-----')
	stock_RS['roc'] = stock_RS['rs'] - stock_RS['rs'].shift(ROCPeriod)

	stock_RS['rs_ema_5']=talib.EMA(stock_RS['rs'],5)
	stock_RS['rs_ema_22'] = talib.EMA(stock_RS['rs'], 22)
	stock_RS['rs_ema_66'] = talib.EMA(stock_RS['rs'], 66)

	stock_RS['roc_ema_5'] = talib.EMA(stock_RS['roc'], 5)
	stock_RS['roc_ema_22'] = talib.EMA(stock_RS['roc'], 22)
	stock_RS['roc_ema_66'] = talib.EMA(stock_RS['roc'], 66)
	print('stock_RS:',stock_RS)
	stock_RS=stockstats.StockDataFrame.retype(stock_RS)

	p1 = figure(width=1750, height=320)
	renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
	draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
	p1.add_tools(draw_tool)
	p1.toolbar.active_drag = draw_tool
	# add renderers
	# stockStat["date"] = pd.to_datetime(stockStat.index.values)
	# ["volume","volume_delta"]

	# 设置20个颜色循环，显示0 2 4 6 号序列。
	p1.xaxis.major_label_overrides = d

	# p1.xaxis.bounds = (0, stockStat.index[-1])
	p1.x_range.range_padding = 0.02

	p1.line(stockStats.index, stock_RS['rs'], color=line_Color[1], legend_label='RS', width=2)
	p1.line(stockStats.index, stock_RS['rs_ema_5'], color=line_Color[2], legend_label='5', width=2)
	p1.line(stockStats.index, stock_RS['rs_ema_22'], color=line_Color[3], legend_label='22', width=2)
	p1.line(stockStats.index, stock_RS['rs_ema_66'], color=line_Color[4], legend_label='66', width=2)

	p1.legend.location = "top_left"
	p1.x_range = p_list[0][0].x_range
	p_list.append([p1])

	p1 = figure(width=1750, height=320)
	renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
	draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
	p1.add_tools(draw_tool)
	p1.toolbar.active_drag = draw_tool
	# add renderers
	# stockStat["date"] = pd.to_datetime(stockStat.index.values)
	# ["volume","volume_delta"]

	# 设置20个颜色循环，显示0 2 4 6 号序列。
	p1.xaxis.major_label_overrides = d

	# p1.xaxis.bounds = (0, stockStat.index[-1])
	p1.x_range.range_padding = 0.02

	p1.line(stockStats.index, stock_RS['roc'], color=line_Color[1], legend_label='ROC', width=2)
	p1.line(stockStats.index, stock_RS['roc_ema_5'], color=line_Color[2], legend_label='5', width=2)
	p1.line(stockStats.index, stock_RS['roc_ema_22'], color=line_Color[3], legend_label='22', width=2)
	p1.line(stockStats.index, stock_RS['roc_ema_66'], color=line_Color[4], legend_label='66', width=2)

	p1.legend.location = "top_left"
	p1.x_range = p_list[0][0].x_range
	p_list.append([p1])

	crosshair = CrosshairTool(dimensions="both")
	for plot in p_list:
		plot[0].add_tools(crosshair)
	return p_list


def fun_none():
	print('wrong type')
	return None


# 增加画图方法
def add_plot(stockStat, stockStat1, conf):
	p_list = []
	# 循环 多个line 信息。

	#p_list = plot_dist.get(conf['mark'], fun_none)(stockStat, stockStat1, conf)
	p_list=plot_RSFactor(stockStat,stockStat1,conf)
	gp = gridplot(p_list)
	script, div = components(gp)
	return {
		"script": script,
		"div": div,
		"title": conf["title"],
		"desc": conf["desc"]
	}
