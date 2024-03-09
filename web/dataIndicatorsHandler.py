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
import numpy as np
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.palettes import Category20
from math import radians
from bokeh.models import DatetimeTickFormatter,FreehandDrawTool,HoverTool,ColumnDataSource,CrosshairTool
import mamingSystem.GetData.FromMySQL.get_daily_market_from_mysql as get_daily_info
import mamingSystem.GetData.FromMySQL.get_daily_index_market_from_mysql as get_index_info
import mamingSystem.GetData.FromMySQL.get_daily_industry_market_from_mysql as get_board_info
import mamingSystem.GetData.FromMySQL.get_daily_ETF_market_from_mysql as get_etf_info
import talib
pd.set_option('display.max_columns', None)

line_Color=['yellow','Fuchsia','Indigo','blue','OrangeRed','black']
# 获得页面数据。
class GetDataIndicatorsHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        codes = self.get_argument("code", default=None, strip=False).split('_')
        print('codes:',codes)
        types=codes[0]
        code=codes[1]
        logging.info(code)
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        comp_list = []

        try:
            date_now = datetime.datetime.now()
            date_end = date_now.strftime("%Y-%m-%d")
            date_start = (date_now + datetime.timedelta(days=-500)).strftime("%Y-%m-%d")
            print(code, date_start, date_end)

            # open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
            # 使用缓存方法。加快计算速度。

            startdate=''.join(date_start.split('-'))
            enddate = ''.join(date_end.split('-'))
            if types=='stock':
                stock=get_daily_info.get_daily_market_qfq_from_dfcf(code, startdate, enddate)
                stock.rename(columns={'deal': 'amount', 'zhenfu': 'amplitude', 'zhangdiefu': 'quote_change','zhangdiee':'ups_downs'},inplace=True)
            #stock = common.get_hist_data_cache(code, date_start, date_end)
            elif types=='index':
                stock=get_index_info.get_daily_index_market_information(code,startdate,enddate)
            elif types=='board':
                stock=get_board_info.get_daily_board_market_bfq_from_dfcf(code,startdate,enddate)
            elif types=='etf':
                stock=get_etf_info.get_ETF_daily_market_information(code,startdate,enddate)
            print(stock)
            logging.info(stock.head(1))

            # print(stock) [186 rows x 14 columns]
            # 初始化统计类
            # stockStat = stockstats.StockDataFrame.retype(pd.read_csv("002032.csv"))
            stockStat = stockstats.StockDataFrame.retype(stock)

            batch_add(comp_list, stockStat)


        except Exception as e:
            logging.info("error :", e)
        logging.info("#################### GetStockHtmlHandlerEnd ####################")

        self.render("stock_indicators.html", comp_list=comp_list,
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))

# 全部指标数据汇总
indicators_all_dic = [
    {
        "title": "1，交易量delta指标分析",
        "desc": "The Volume Delta (Vol ∆) ",
        "dic": ["volume", "volume_delta"]
    }, {
        "title": "2，计算n天差",
        "desc": "可以计算，向前n天，和向后n天的差。",
        "dic": ["close", "close_1_d", "close_2_d", "close_-1_d", "close_-2_d"]
    }, {
        "title": "3，n天涨跌百分百计算",
        "desc": "可以看到，-n天数据和今天数据的百分比。",
        "dic": ["close", "close_-1_r", "close_-2_r"]
    }, {
        "title": "4，CR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/CR%E6%8C%87%E6%A0%87 价格动量指标
            4. CR跌穿a、b、c、d四条线，再由低点向上爬升160时，为短线获利的一个良机，应适当卖出股票。
            5. CR跌至40以下时，是建仓良机。而CR高于300~400时，应注意适当减仓。
        """,
        "dic": ["close","cr","cr-ma1","cr-ma2","cr-ma3"]
    }, {
        "title": "5，最大值，最小值",
        "desc": """
            计算区间最大值
            volume max of three days ago, yesterday and two days later
            stock["volume_-3,2,-1_max"]
            volume min between 3 days ago and tomorrow
            stock["volume_-3~1_min"]
            实际使用的时候使用 -2~2 可计算出5天的最大，最小值。
        """,
        "dic": ["volume","volume_-2~2_max","volume_-2~2_min"]
    }, {
        "title": "6，KDJ指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87
            随机指标(KDJ)一般是根据统计学的原理，通过一个特定的周期（常为9日、9周等）内出现过的最高价、最低价及最后一个计算周期的收盘价及这三者之间的比例关系，来计算最后一个计算周期的未成熟随机值RSV，然后根据平滑移动平均线的方法来计算K值、D值与J值，并绘成曲线图来研判股票走势。
            （3）在使用中，常有J线的指标，即3乘以K值减2乘以D值（3K－2D＝J），其目的是求出K值与D值的最大乖离程度，以领先KD值找出底部和头部。J大于100时为超买，小于10时为超卖。
        """,
        "dic": ["close","kdjk","kdjd","kdjj"]
    }, {
        "title": "7，SMA指标",
        "desc": """
            http://wiki.mbalib.com/wiki/Sma
            简单移动平均线（Simple Moving Average，SMA）
            可以动态输入参数，获得几天的移动平均。
        """,
        "dic": ["close","close_5_sma","close_10_sma"]
    }, {
        "title": "8，MACD指标",
        "desc": """
            http://wiki.mbalib.com/wiki/MACD
            平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标
            MACD
            stock["macd"]
            MACD signal line
            stock["macds"]
            MACD histogram
            stock["macdh"]
            MACD技术分析，运用DIF线与MACD线之相交型态及直线棒高低点与背离现象，作为买卖讯号，尤其当市场股价走势呈一较为明确波段趋势时，
            MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。
            当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。
        """,
        "dic": ["close","macd","macds","macdh"]
    }, {
        "title": "9，BOLL指标",
        "desc": """
        http://wiki.mbalib.com/wiki/BOLL
            布林线指标(Bollinger Bands)
            bolling, including upper band and lower band
            stock["boll"]
            stock["boll_ub"]
            stock["boll_lb"]
            1、当布林线开口向上后，只要股价K线始终运行在布林线的中轨上方的时候，说明股价一直处在一个中长期上升轨道之中，这是BOLL指标发出的持股待涨信号，如果TRIX指标也是发出持股信号时，这种信号更加准确。此时，投资者应坚决持股待涨。
            2、当布林线开口向下后，只要股价K线始终运行在布林线的中轨下方的时候，说明股价一直处在一个中长期下降轨道之中，这是BOLL指标发出的持币观望信号，如果TRIX指标也是发出持币信号时，这种信号更加准确。此时，投资者应坚决持币观望。
        """,
        "dic": ["close","boll","boll_ub","boll_lb"]
    }, {
        "title": "10，RSI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/RSI
            相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数
            6 days RSI
            stock["rsi_6"]
            12 days RSI
            stock["rsi_12"]
            （2）强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场。
            （3）强弱指标多在70与30之间波动。当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。
            （4）当六日强弱指标下降至20时，表示股市有超卖现象，如果一旦继续下降至10以下时则表示已到严重超卖区域，股价极可能有止跌回升的机会。
        """,
        "dic": ["close","rsi_6","rsi_12"]
    }, {
        "title": "11，WR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E5%A8%81%E5%BB%89%E6%8C%87%E6%A0%87
            威廉指数（Williams%Rate）该指数是利用摆动点来度量市场的超买超卖现象。
            10 days WR
            stock["wr_10"]
            6 days WR
            stock["wr_6"]
        """,
        "dic": ["close","wr_10","wr_6"]
    }, {
        "title": "12，CCI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87
            顺势指标又叫CCI指标，其英文全称为“Commodity Channel Index”，
            是由美国股市分析家唐纳德·蓝伯特（Donald Lambert）所创造的，是一种重点研判股价偏离度的股市分析工具。
             CCI, default to 14 days
            stock["cci"]
             20 days CCI
            stock["cci_20"]
            1、当CCI指标从下向上突破﹢100线而进入非常态区间时，表明股价脱离常态而进入异常波动阶段，
              中短线应及时买入，如果有比较大的成交量配合，买入信号则更为可靠。
            2、当CCI指标从上向下突破﹣100线而进入另一个非常态区间时，表明股价的盘整阶段已经结束，
              将进入一个比较长的寻底过程，投资者应以持币观望为主。
        """,
        "dic": ["close","cci","cci_20"]
    }, {
        "title": "13，TR、ATR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E5%9D%87%E5%B9%85%E6%8C%87%E6%A0%87
            均幅指标（Average True Ranger,ATR）
            均幅指标（ATR）是取一定时间周期内的股价波动幅度的移动平均值，主要用于研判买卖时机。
            TR (true range)
            stock["tr"]
             ATR (Average True Range)
            stock["atr"]
            均幅指标无论是从下向上穿越移动平均线，还是从上向下穿越移动平均线时，都是一种研判信号。
        """,
        "dic": ["close","tr","atr"]
    }, {
        "title": "14，DMA指标",
        "desc": """
            http://wiki.mbalib.com/wiki/DMA
            DMA指标（Different of Moving Average）又叫平行线差指标，是目前股市分析技术指标中的一种中短期指标，它常用于大盘指数和个股的研判。
            DMA, difference of 10 and 50 moving average
            stock["dma"]
        """,
        "dic": ["close","dma"]
    }, {
        "title": "15，DMI，+DI，-DI，DX，ADX，ADXR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/DMI
            动向指数Directional Movement Index,DMI）
            http://wiki.mbalib.com/wiki/ADX
            平均趋向指标（Average Directional Indicator，简称ADX）
            http://wiki.mbalib.com/wiki/%E5%B9%B3%E5%9D%87%E6%96%B9%E5%90%91%E6%8C%87%E6%95%B0%E8%AF%84%E4%BC%B0
            平均方向指数评估（ADXR）实际是今日ADX与前面某一日的ADX的平均值。ADXR在高位与ADX同步下滑，可以增加对ADX已经调头的尽早确认。
            ADXR是ADX的附属产品，只能发出一种辅助和肯定的讯号，并非入市的指标，而只需同时配合动向指标(DMI)的趋势才可作出买卖策略。
            在应用时，应以ADX为主，ADXR为辅。
        """,
        "dic": ["close","pdi","mdi","dx","adx","adxr"]
    }, {
        "title": "16，TRIX，MATRIX指标",
        "desc": """
            http://wiki.mbalib.com/wiki/TRIX
            TRIX指标又叫三重指数平滑移动平均指标（Triple Exponentially Smoothed Average）
        """,
        "dic": ["close","trix","trix_9_sma"]
    }, {
        "title": "17，VR，MAVR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E6%88%90%E4%BA%A4%E9%87%8F%E6%AF%94%E7%8E%87
            成交量比率（volume Ratio，VR）（简称VR），是一项通过分析股价上升日成交额（或成交量，下同）与股价下降日成交额比值，
            从而掌握市场买卖气势的中期技术指标。
             VR, default to 26 days
            stock["vr"]
             MAVR is the simple moving average of VR
            stock["vr_6_sma"]
        """,
        "dic": ["close","vr","vr_6_sma"]
    }
]
# 配置数据
indicators_dic = [
     {
        "title": "6，KDJ指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87
            随机指标(KDJ)一般是根据统计学的原理，通过一个特定的周期（常为9日、9周等）内出现过的最高价、最低价及最后一个计算周期的收盘价及这三者之间的比例关系，来计算最后一个计算周期的未成熟随机值RSV，然后根据平滑移动平均线的方法来计算K值、D值与J值，并绘成曲线图来研判股票走势。
            （3）在使用中，常有J线的指标，即3乘以K值减2乘以D值（3K－2D＝J），其目的是求出K值与D值的最大乖离程度，以领先KD值找出底部和头部。J大于100时为超买，小于10时为超卖。
        """,
        "dic": ["close","kdjk","kdjd","kdjj"]
    }, {
        "title": "7，SMA指标",
        "desc": """
            http://wiki.mbalib.com/wiki/Sma
            简单移动平均线（Simple Moving Average，SMA）
            可以动态输入参数，获得几天的移动平均。
        """,
        "dic": ["close","close_5_sma","close_10_sma"]
    }, {
        "title": "8，MACD指标",
        "desc": """
            http://wiki.mbalib.com/wiki/MACD
            平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标
            MACD
            stock["macd"]
            MACD signal line
            stock["macds"]
            MACD histogram
            stock["macdh"]
            MACD技术分析，运用DIF线与MACD线之相交型态及直线棒高低点与背离现象，作为买卖讯号，尤其当市场股价走势呈一较为明确波段趋势时，
            MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。
            当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。
        """,
        "dic": ["close","macd","macds","macdh"]
    }, {
        "title": "9，BOLL指标",
        "desc": """
        http://wiki.mbalib.com/wiki/BOLL
            布林线指标(Bollinger Bands)
            bolling, including upper band and lower band
            stock["boll"]
            stock["boll_ub"]
            stock["boll_lb"]
            1、当布林线开口向上后，只要股价K线始终运行在布林线的中轨上方的时候，说明股价一直处在一个中长期上升轨道之中，这是BOLL指标发出的持股待涨信号，如果TRIX指标也是发出持股信号时，这种信号更加准确。此时，投资者应坚决持股待涨。
            2、当布林线开口向下后，只要股价K线始终运行在布林线的中轨下方的时候，说明股价一直处在一个中长期下降轨道之中，这是BOLL指标发出的持币观望信号，如果TRIX指标也是发出持币信号时，这种信号更加准确。此时，投资者应坚决持币观望。
        """,
        "dic": ["close","boll","boll_ub","boll_lb"]
    }, {
        "title": "10，RSI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/RSI
            相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数
            6 days RSI
            stock["rsi_6"]
            12 days RSI
            stock["rsi_12"]
            （2）强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场。
            （3）强弱指标多在70与30之间波动。当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。
            （4）当六日强弱指标下降至20时，表示股市有超卖现象，如果一旦继续下降至10以下时则表示已到严重超卖区域，股价极可能有止跌回升的机会。
        """,
        "dic": ["close","rsi_6","rsi_12"]
    },{
        "title": "12，CCI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87
            顺势指标又叫CCI指标，其英文全称为“Commodity Channel Index”，
            是由美国股市分析家唐纳德·蓝伯特（Donald Lambert）所创造的，是一种重点研判股价偏离度的股市分析工具。
             CCI, default to 14 days
            stock["cci"]
             20 days CCI
            stock["cci_20"]
            1、当CCI指标从下向上突破﹢100线而进入非常态区间时，表明股价脱离常态而进入异常波动阶段，
              中短线应及时买入，如果有比较大的成交量配合，买入信号则更为可靠。
            2、当CCI指标从上向下突破﹣100线而进入另一个非常态区间时，表明股价的盘整阶段已经结束，
              将进入一个比较长的寻底过程，投资者应以持币观望为主。
        """,
        "dic": ["close","cci","cci_20"]
    }
]

indicators_dic_myself=[
    {
        "title": "1，ROC指标计算n天差",
        "desc": "可以计算，向前n天，和向后n天的差。",
        "mark":"ROC",
        "dic": ["close", "close_-5_d", "close_-10_d", "close_-22_d"]
    }, {
        "title": "2，EMA指标",
        "desc": """
           http://wiki.mbalib.com/wiki/Sma
           指数移动平均线（EMA）
           可以动态输入参数，获得几天的移动平均。
       """,
        "mark":"EMA",
        "dic": ["close", "close_10_ema", "close_22_ema","close_66_ema"]
    }, {
        "title": "3，MACD指标",
        "desc": """
           http://wiki.mbalib.com/wiki/MACD
           平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标
           MACD
           stock["macd"]
           MACD signal line
           stock["macds"]
           MACD histogram
           stock["macdh"]
           MACD技术分析，运用DIF线与MACD线之相交型态及直线棒高低点与背离现象，作为买卖讯号，尤其当市场股价走势呈一较为明确波段趋势时，
           MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。
           当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。
       """,
        "mark":"MACD",
        "dic": ["close", "macd", "macds", "macdh"]
    }, {
        "title": "4，BOLL指标",
        "desc": """
       http://wiki.mbalib.com/wiki/BOLL
           布林线指标(Bollinger Bands)
           bolling, including upper band and lower band
           stock["boll"]
           stock["boll_ub"]
           stock["boll_lb"]
           1、当布林线开口向上后，只要股价K线始终运行在布林线的中轨上方的时候，说明股价一直处在一个中长期上升轨道之中，这是BOLL指标发出的持股待涨信号，如果TRIX指标也是发出持股信号时，这种信号更加准确。此时，投资者应坚决持股待涨。
           2、当布林线开口向下后，只要股价K线始终运行在布林线的中轨下方的时候，说明股价一直处在一个中长期下降轨道之中，这是BOLL指标发出的持币观望信号，如果TRIX指标也是发出持币信号时，这种信号更加准确。此时，投资者应坚决持币观望。
           StockDataFrame.BOLL_STD_TIMES. The default value is 2.
       """,
        "mark":"BOLL",
        "dic": ["close", "boll", "boll_ub", "boll_lb"]
    }, {
        "title": "5，RSI指标",
        "desc": """
           http://wiki.mbalib.com/wiki/RSI
           相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数
           6 days RSI
           stock["rsi_6"]
           12 days RSI
           stock["rsi_12"]
           （2）强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场。
           （3）强弱指标多在70与30之间波动。当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。
           （4）当六日强弱指标下降至20时，表示股市有超卖现象，如果一旦继续下降至10以下时则表示已到严重超卖区域，股价极可能有止跌回升的机会。
       """,
        "mark":"RSI",
        "dic": ["close", "rsi_5","rsi_22","rsi_60"]
    }, {
        "title": "6，TR、ATR指标",
        "desc": """
           http://wiki.mbalib.com/wiki/%E5%9D%87%E5%B9%85%E6%8C%87%E6%A0%87
           均幅指标（Average True Ranger,ATR）
           均幅指标（ATR）是取一定时间周期内的股价波动幅度的移动平均值，主要用于研判买卖时机。
           TR (true range)
           stock["tr"]
            ATR (Average True Range)
           stock["atr"]
           均幅指标无论是从下向上穿越移动平均线，还是从上向下穿越移动平均线时，都是一种研判信号。
       """,
        "mark":'ATR',
        "dic": ["close", "tr", "atr"]
    }, {
        "title": "7，KDJ指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87
            随机指标(KDJ)一般是根据统计学的原理，通过一个特定的周期（常为9日、9周等）内出现过的最高价、最低价及最后一个计算周期的收盘价及这三者之间的比例关系，来计算最后一个计算周期的未成熟随机值RSV，然后根据平滑移动平均线的方法来计算K值、D值与J值，并绘成曲线图来研判股票走势。
            （3）在使用中，常有J线的指标，即3乘以K值减2乘以D值（3K－2D＝J），其目的是求出K值与D值的最大乖离程度，以领先KD值找出底部和头部。J大于100时为超买，小于10时为超卖。
        """,
        "mark":"KDJ",
        "dic": ["close","kdjk","kdjd","kdjj"]
    }
]

# 批量添加数据。
def batch_add(comp_list, stockStat):
    for conf in indicators_dic_myself:
        #logging.info(conf)
        print('conf:',conf)
        comp_list.append(add_plot(stockStat, conf))

#"dic": ["close", "close_-5_d", "close_-10_d", "close_-22_d"]
def plot_ROC(stockStat,conf):

    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)


    p1 = figure(width=1750, height=600, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes=list(stockStat['close'])

    '''
        p1.add_tools(HoverTool(tooltips=[
            ("(close,open)", "(@close, @open)"),
            ("volume", "@volume"), ]))
        '''

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")
    p_list.append([p1])

    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])

    p1 = figure(width=1750, height=360, title='ROC')
    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    # add renderers
    # stockStat["date"] = pd.to_datetime(stockStat.index.values)
    # ["volume","volume_delta"]

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }

    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    for key, val in enumerate(conf["dic"]):
        logging.info(key)
        logging.info(val)

        if key!=0:
            # p1 = figure(width=1000, height=250, x_axis_type="datetime",title=val)
            p1.line(stockStats.index, stockStat[val], color=line_Color[key],legend_label=val.split('_')[1],width=2)


            # Set date format for x axis 格式化。
            # p1.xaxis.formatter = DatetimeTickFormatter(hours=["%Y-%m-%d"], days=["%Y-%m-%d"],months=["%Y-%m-%d"], years=["%Y-%m-%d"])
            # p1.xaxis.major_label_orientation = radians(30) #可以旋转一个角度。
    p1.legend.location = "top_left"
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list

#"dic": ["close", "close_10_ema", "close_22_ema","close_66_ema"]
def plot_EMA(stockStat,conf):

    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)


    p1 = figure(width=1750, height=800, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes=list(stockStat['close'])

    #p1.add_tools(HoverTool(tooltips= [("(close,open)", "(@close, @open)"),("volume", "@volume"),]))

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")

    for key, val in enumerate(conf["dic"]):
        logging.info(key)
        logging.info(val)

        if key!=0:
            # p1 = figure(width=1000, height=250, x_axis_type="datetime",title=val)
            p1.line(stockStats.index, stockStat[val], color=line_Color[key],legend_label='EMA'+val.split('_')[1],width=3)


            # Set date format for x axis 格式化。
            # p1.xaxis.formatter = DatetimeTickFormatter(hours=["%Y-%m-%d"], days=["%Y-%m-%d"],months=["%Y-%m-%d"], years=["%Y-%m-%d"])
            # p1.xaxis.major_label_orientation = radians(30) #可以旋转一个角度。
    p1.legend.location = "top_left"
    p_list.append([p1])

    p1 = figure(width=1750, height=260 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    vol_5=talib.SMA(stockStat.volume,5)
    vol_10=talib.SMA(stockStat.volume,10)
    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.line(stockStats.index, vol_5, color='black', legend_label='vol_sma_5', width=3)
    p1.line(stockStats.index, vol_10, color='blue', legend_label='vol_sma_10', width=3)
    p1.legend.location = "top_left"
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])

    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list

#"dic": ["close", "macd", "macds", "macdh"]
def plot_MACD(stockStat,conf):
    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)

    p1 = figure(width=1750, height=600, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes = list(stockStat['close'])
    '''
    p1.add_tools(HoverTool(tooltips=[
        ("(close,open)", "(@close, @open)"),
        ("volume", "@volume"), ]))
    '''

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    print(stockStat.volume)
    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=360, title='MACD')
    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    # add renderers
    # stockStat["date"] = pd.to_datetime(stockStat.index.values)
    # ["volume","volume_delta"]

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }

    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    p1.line(stockStats.index, stockStat['macd'], color=line_Color[1], legend_label='macd', width=2)
    p1.line(stockStats.index, stockStat['macds'], color=line_Color[2], legend_label='macds', width=2)
    p1.vbar(x=stockStats.index, top=stockStat['macdh'], color=line_Color[3], legend_label='macdh',width=0.5,bottom=0)

    p1.legend.location = "top_left"
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list

#StockDataFrame.BOLL_STD_TIMES. The default value is 2.
#"dic": ["close", "boll", "boll_ub", "boll_lb"]

def plot_BOLL(stockStat,conf):

    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)


    p1 = figure(width=1750, height=900, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes=list(stockStat['close'])

    #p1.add_tools(HoverTool(tooltips= [("(close,open)", "(@close, @open)"),("volume", "@volume"),]))

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")

    p1.line(stockStats.index, stockStat['boll'], color=line_Color[1], legend_label='boll-22-2', width=3)
    p1.line(stockStats.index, stockStat['boll_ub'], color=line_Color[2], width=3)
    p1.line(stockStats.index, stockStat['boll_lb'], color=line_Color[3], width=3)

    p1.legend.location = "top_left"
    p_list.append([p1])

    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])

    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list
#"dic": ["close", "rsi_5","rsi_22","rsi_60"]
def plot_RSI(stockStat,conf):
    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)

    p1 = figure(width=1750, height=600, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes = list(stockStat['close'])
    '''
    p1.add_tools(HoverTool(tooltips=[
        ("(close,open)", "(@close, @open)"),
        ("volume", "@volume"), ]))
    '''

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=360, title='RSI')
    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    # add renderers
    # stockStat["date"] = pd.to_datetime(stockStat.index.values)
    # ["volume","volume_delta"]

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }

    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    for key, val in enumerate(conf["dic"]):

        if key != 0:
            # p1 = figure(width=1000, height=250, x_axis_type="datetime",title=val)
            p1.line(stockStats.index, stockStat[val], color=line_Color[key], legend_label=val, width=2)

    p1.legend.location = "top_left"
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list
#"dic": ["close", "tr", "atr"] atr_22  "close_22_ema"
def plot_ATR(stockStat,conf):

    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)


    p1 = figure(width=1750, height=900, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes=list(stockStat['close'])

    #p1.add_tools(HoverTool(tooltips= [("(close,open)", "(@close, @open)"),("volume", "@volume"),]))

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")

    p1.line(stockStats.index, stockStat["close_22_ema"], color=line_Color[1], legend_label="close_22_ema", width=3)
    p1.line(stockStats.index, stockStat["close_22_ema"]+stockStat['atr_22'], legend_label="up_atr_22",color=line_Color[2], width=3)
    p1.line(stockStats.index, stockStat["close_22_ema"]-stockStat['atr_22'], legend_label="down_atr_22",color=line_Color[3], width=3)

    p1.legend.location = "top_left"
    p_list.append([p1])

    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color='red')
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])

    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list

#"close","kdjk","kdjd","kdjj"
def plot_KDJ(stockStat,conf):

    p_list = []

    # 循环 多个line 信息。

    # stockStat.reset_index()
    stockStats = pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)

    p1 = figure(width=1750, height=600, title='close', y_axis_type="log")

    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    closes = list(stockStat['close'])
    '''
    p1.add_tools(HoverTool(tooltips=[
        ("(close,open)", "(@close, @open)"),
        ("volume", "@volume"), ]))
    '''

    inc = stockStat.close > stockStat.open
    dec = stockStat.open >= stockStat.close

    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    w = 0.5

    p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
    p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green",
            line_color="green")
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=160 )

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }
    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02
    print(stockStat.volume)
    p1.vbar(stockStats.index[inc], w, 0, stockStat.volume[inc], fill_color="red",
            line_color="red")
    p1.vbar(stockStats.index[dec], w, 0, stockStat.volume[dec], fill_color="green",
            line_color="green")
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    '''
    p1 = figure(width=1750, height=360, title='KDJ')
    renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
    p1.add_tools(draw_tool)
    p1.toolbar.active_drag = draw_tool
    # add renderers
    # stockStat["date"] = pd.to_datetime(stockStat.index.values)
    # ["volume","volume_delta"]

    # 设置20个颜色循环，显示0 2 4 6 号序列。
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
    }

    # p1.xaxis.bounds = (0, stockStat.index[-1])
    p1.x_range.range_padding = 0.02

    p1.line(stockStats.index, stockStat['kdjk'], color=line_Color[1], legend_label='K', width=2)
    p1.line(stockStats.index, stockStat['kdjd'], color=line_Color[2], legend_label='D', width=2)
    p1.line(stockStats.index, stockStat['kdjj'], color=line_Color[3], legend_label='J', width=2)

    p1.legend.location = "top_left"
    p1.x_range = p_list[0][0].x_range
    p_list.append([p1])
    crosshair = CrosshairTool(dimensions="both")
    for plot in p_list:
        plot[0].add_tools(crosshair)
    return p_list

plot_dist={
    'ROC':plot_ROC,
    'EMA':plot_EMA,
    'MACD':plot_MACD,
    'BOLL':plot_BOLL,
    'RSI':plot_RSI,
    'ATR':plot_ATR,
    'KDJ':plot_KDJ,
}



def fun_none():
    print('wrong type')
    return None

# 增加画图方法
def add_plot(stockStat, conf):
    p_list = []
    logging.info("############################", type(conf["dic"]))
    # 循环 多个line 信息。


    p_list=plot_dist.get(conf['mark'],fun_none)(stockStat,conf)
    gp = gridplot(p_list)
    script, div = components(gp)
    return {
        "script": script,
        "div": div,
        "title": conf["title"],
        "desc": conf["desc"]
    }

    #stockStat.reset_index()
    stockStats=pd.DataFrame(stockStat.index)
    stockStats.reset_index(inplace=True)

    for key, val in enumerate(conf["dic"]):
        logging.info(key)
        logging.info(val)

        if val=='close':

            p1 = figure(width=1000, height=450, title=val,y_axis_type="log")

            renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
            draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
            p1.add_tools(draw_tool)
            p1.toolbar.active_drag = draw_tool

            # add renderers
            #stockStat["date"] = pd.to_datetime(stockStat.index.values)
            # map dataframe indices to date strings and use as label overrides

            #p1.xaxis.bounds = (0, stockStat.index[-1])
            inc = stockStat.close > stockStat.open
            dec = stockStat.open > stockStat.close
            #w = 12 * 60 * 60 * 1000
            #p1.x_range.range_padding = 0.02
            p1.xaxis.major_label_overrides = {
                i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
            }
            #p1.xaxis.bounds = (0, stockStat.index[-1])
            p1.x_range.range_padding = 0.02
            w=0.5

            p1.segment(stockStats.index, stockStat.high, stockStats.index, stockStat.low, color="black")
            p1.vbar(stockStats.index[inc], w, stockStat.open[inc], stockStat.close[inc], fill_color="red", line_color="red")
            p1.vbar(stockStats.index[dec], w, stockStat.open[dec], stockStat.close[dec], fill_color="green", line_color="green")
            '''
            p1.add_tools(HoverTool(
                tooltips=[
                    ('date', '@date{%F}'),
                    ('open', '$@{open}{%0.2f}'),  # use @{ } for field names with spaces
                    ('high', '$@{high}{%0.2f}'),
                    ('low', '$@{low}{%0.2f}'),
                    ('close', '$@{close}{%0.2f}'),
                    ('volume', '@volume{0.00 a}'),
                ],

                formatters={
                    '@date': 'datetime',  # use 'datetime' formatter for '@date' field
                    '@{adj close}': 'printf',  # use 'printf' formatter for '@{adj close}' field
                    '@{adj open}': 'printf',
                    '@{adj high}': 'printf',
                    '@{adj low}': 'printf',
                    # use default 'numeral' formatter for other fields
                },

                # display a tooltip whenever the cursor is vertically in line with a glyph
                mode='vline'
            ))
            '''
        else:
            #p1 = figure(width=1000, height=250, x_axis_type="datetime",title=val)
            p1 = figure(width=1000, height=250, title=val)
            renderer = p1.multi_line(line_width=3, alpha=0.4, color='red')
            draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=10)
            p1.add_tools(draw_tool)
            p1.toolbar.active_drag = draw_tool
            # add renderers
            #stockStat["date"] = pd.to_datetime(stockStat.index.values)
            # ["volume","volume_delta"]

            # 设置20个颜色循环，显示0 2 4 6 号序列。
            p1.xaxis.major_label_overrides = {
                i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(stockStats["date"]))
            }

            #p1.xaxis.bounds = (0, stockStat.index[-1])
            p1.x_range.range_padding = 0.02
            p1.line(stockStats.index, stockStat[val], color=Category20[20][key * 2])

            if key!=0:
                p1.x_range=p_list[0][0].x_range
            # Set date format for x axis 格式化。
            #p1.xaxis.formatter = DatetimeTickFormatter(hours=["%Y-%m-%d"], days=["%Y-%m-%d"],months=["%Y-%m-%d"], years=["%Y-%m-%d"])
            # p1.xaxis.major_label_orientation = radians(30) #可以旋转一个角度。

        p_list.append([p1])


    gp = gridplot(p_list)
    script, div = components(gp)
    return {
        "script": script,
        "div": div,
        "title": conf["title"],
        "desc": conf["desc"]
    }
