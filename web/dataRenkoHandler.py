#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from tornado import gen
import web.base as webBase
import logging

import datetime
import libs.common as common

import pandas as pd

import base64
import io

import mplfinance as mpf

import mamingSystem.GetData.FromMySQL.get_daily_market_from_mysql as get_daily_info
import mamingSystem.GetData.FromMySQL.get_daily_index_market_from_mysql as get_index_info
import mamingSystem.GetData.FromMySQL.get_daily_industry_market_from_mysql as get_board_info
import mamingSystem.GetData.FromMySQL.get_daily_ETF_market_from_mysql as get_etf_info

#pd.set_option('display.max_columns', None)

line_Color = ['yellow', 'Fuchsia', 'Indigo', 'blue', 'OrangeRed', 'black']
cncolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
# Create a new style based on `nightclouds` but with my own `marketcolors`:
CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor,rc={'font.family':'SimHei'})

# 获得页面数据。
class GetDataRenkoHandler(webBase.BaseHandler):
	@gen.coroutine
	def get(self):
		codes = self.get_argument("code", default=None, strip=False).split('_')

		types = codes[0]
		code = codes[1]

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
			stock=pd.DataFrame()
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

			stock['date'] = stock['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
			stock.rename(columns={'date': 'datetime'}, inplace=True)
			stock['datetime'] = pd.to_datetime(stock['datetime'])
			stock.set_index(['datetime'], inplace=True)
			print('stock:',stock)
			buf=io.BytesIO()

			mpf.plot(stock, style=CN, type='renko', pnf_params=dict(box_size='atr', atr_length=10), mav=(5, 10, 20),
					 volume=True,panel_ratios=(4, 1), figscale=0.8, axtitle=types + code,savefig=dict(fname=buf, dpi=250, pad_inches=0.25),
					 scale_padding={'left': 0.5, 'top':0.5, 'right': 0.5, 'bottom':0.5},xrotation=10)
			photo_data=base64.b64encode(buf.getbuffer()).decode('ascii')
			#print('url:',f"<img src='data:image/png;base64,{photo_data}' align='middle'/>")
			comp_list.append({"img": f"<img src='data:image/png;base64,{photo_data}'/>","title": 'Renko',	"desc": 'Renko'})

		except Exception as e:
			logging.info("error :", e)


		logging.info("#################### GetStockHtmlHandlerEnd ####################")

		self.render("stock_renko.html", comp_list=comp_list,
				pythonStockVersion=common.__version__,
				leftMenu=webBase.GetLeftMenu(self.request.uri))