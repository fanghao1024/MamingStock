#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from tornado import gen
import libs.common as common
import libs.stock_web_dic as stock_web_dic
import web.base as webBase
import logging
import datetime
import pandas as pd
import akshare as ak

# info 蓝色 云财经
# success 绿色
#  danger 红色 东方财富
#  warning 黄色
WEB_EASTMONEY_URL = u"""
    <a class='btn btn-danger btn-xs tooltip-danger' data-rel="tooltip" data-placement="right" data-original-title="东方财富，股票详细地址，新窗口跳转。"
    href='http://quote.eastmoney.com/%s.html' target='_blank'>东财</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showIndicatorsWindow('%s');">指标</a>
    
    <a class='btn btn-warning btn-xs tooltip-warning' data-rel="tooltip" data-placement="right" data-original-title="东方财富，研报地址，本地弹窗窗口。"
    onclick="showDFCFWindow('%s');">东研</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showWeeklyLineWindow('%s');">周线</a>
    
    <a class='btn btn-warning btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showPNFWindow('%s');">PNF</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showRenkoWindow('%s');">RENKO</a>
    
    <a class='btn btn-warning btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showRSWindow('%s');">RS</a>
    
    """
WEB_EASTMONEY_BOARD_URL = u"""
    <a class='btn btn-danger btn-xs tooltip-danger' data-rel="tooltip" data-placement="right" data-original-title="东方财富，股票详细地址，新窗口跳转。"
    href='http://quote.eastmoney.com/bk/90.%s.html' target='_blank'>东财</a>

    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showIndicatorsWindow('%s');">指标</a>

    <a class='btn btn-warning btn-xs tooltip-warning' data-rel="tooltip" data-placement="right" data-original-title="东方财富，研报地址，本地弹窗窗口。"
    onclick="showDFCFWindow('%s');">东研</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showWeeklyLineWindow('%s');">周线</a>
    
    <a class='btn btn-warning btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showPNFWindow('%s');">PNF</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showRenkoWindow('%s');">RENKO</a>
    
    <a class='btn btn-warning btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showRSWindow('%s');">RS</a>

    """
# 和在dic中的字符串一致。字符串前面都不特别声明是u""
eastmoney_name = "查看股票"
kind_table={
    'dailyline':'stock',
    'indexline':'index',
    'industryline':'board',
    'etf_market':'etf',
    'stock_sina_lhb_ggtj':'stock_sina_lhb_ggtj',
    'stock_zh_ah_name':'stock_zh_ah_name'
}

datas =  pd.read_csv('../data/read_data/code_name.csv',converters={u'代码':str})
#datas=ak.stock_zh_a_spot_em()
datas = datas[['代码', '名称']]

#datas.to_csv('code_name.csv')
stock_code_name = {str(datas.iloc[i][0]): datas.iloc[i][1] for i in range(len(datas))}



# 获得页面数据。
class GetStockHtmlHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        stockWeb = stock_web_dic.STOCK_WEB_DATA_MAP[name]
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        date_now = datetime.datetime.now()
        date_now_str = date_now.strftime("%Y%m%d")
        # 每天的 16 点前显示昨天数据。
        if date_now.hour < 16:
            date_now_str = (date_now + datetime.timedelta(days=-1)).strftime("%Y%m%d")

        try:
            # 增加columns 字段中的【查看股票 东方财富】

            logging.info(eastmoney_name in stockWeb.column_names)
            if eastmoney_name in stockWeb.column_names:
                tmp_idx = stockWeb.column_names.index(eastmoney_name)
                logging.info(tmp_idx)
                try:
                    # 防止重复插入数据。可能会报错。
                    stockWeb.columns.remove("eastmoney_url")
                except Exception as e:
                    print("error :", e)
                stockWeb.columns.insert(tmp_idx, "eastmoney_url")

        except Exception as e:
            print("error :", e)
        logging.info("####################GetStockHtmlHandlerEnd")

        self.render("stock_web.html", stockWeb=stockWeb, date_now=date_now_str,
                    pythonStockVersion=common.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))

def process_dailyline(stock_web_list,name_param,type_param,stock_web):
    for tmp_obj in (stock_web_list):
        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]

        try:
            # 增加columns 字段中的【东方财富】
            #logging.info("eastmoney_name : %s " % eastmoney_name)
            #dailyline数据库表里没有股票名称，这里加上
            tmp_obj['name'] = stock_code_name[tmp_obj["code"]]

            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)

                code_tmp = tmp_obj["code"]

                # 判断上海还是 深圳，东方财富 接口要求。

                if code_tmp.startswith("6"):
                    code_tmp = "SH" + code_tmp
                else:
                    code_tmp = "SZ" + code_tmp

                tmp_url = WEB_EASTMONEY_URL % (
                tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])

        except Exception as e:
            print("error1 :", e)
    return stock_web_list
def process_index(stock_web_list,name_param,type_param,stock_web):
    for tmp_obj in (stock_web_list):
        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
        try:
            # 增加columns 字段中的【东方财富】
            logging.info("eastmoney_name : %s " % eastmoney_name)

            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)
                code_tmp = tmp_obj["code"]

                code_tmp = 'zs' + code_tmp
                tmp_url = WEB_EASTMONEY_URL % (
                tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])

        except Exception as e:
            print("error1 :", e)
    return stock_web_list
def process_board(stock_web_list,name_param,type_param,stock_web):
    for tmp_obj in (stock_web_list):
        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
        try:
            # 增加columns 字段中的【东方财富】
            logging.info("eastmoney_name : %s " % eastmoney_name)

            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)
                code_tmp = tmp_obj["code"]
                # 判断上海还是 深圳，东方财富 接口要求。

                tmp_url = WEB_EASTMONEY_BOARD_URL % (
                tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])

        except Exception as e:
            print("error1 :", e)
    return stock_web_list
def process_etf(stock_web_list,name_param,type_param,stock_web):
    for tmp_obj in (stock_web_list):
        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
        # logging.info(tmp_obj)
        try:
            # 增加columns 字段中的【东方财富】
            logging.info("eastmoney_name : %s " % eastmoney_name)

            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)

                code_tmp = tmp_obj["code"]

                tmp_url = WEB_EASTMONEY_URL % (
                tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])
        except Exception as e:
            print("error1 :", e)
    return stock_web_list
def process_stock_sina_lhb_ggtj(stock_web_list,name_param,type_param,stock_web):
    for tmp_obj in (stock_web_list):

        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
        # logging.info(tmp_obj)
        try:
            # 增加columns 字段中的【东方财富】
            logging.info("eastmoney_name : %s " % eastmoney_name)


            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)

                code_tmp = tmp_obj["code"]

                # 判断上海还是 深圳，东方财富 接口要求。

                if code_tmp.startswith("6"):
                    code_tmp = "SH" + code_tmp
                else:
                    code_tmp = "SZ" + code_tmp

                name_param='dailyline'
                tmp_url = WEB_EASTMONEY_URL % (
                tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                # print('tmp_url:')
                # print(tmp_url)
                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])
                # logging.info(type(tmp_obj))
                # tmp.column_names.insert(tmp_idx, eastmoney_name)
        except Exception as e:
            print("error1 :", e)
    return stock_web_list
def process_stock_zh_ah_name(stock_web_list,name_param,type_param,stock_web):
    return process_dailyline(stock_web_list, 'dailyline', type_param, stock_web)
    for tmp_obj in (stock_web_list):

        if type_param == "editor":
            tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
        # logging.info(tmp_obj)
        try:
            # 增加columns 字段中的【东方财富】
            logging.info("eastmoney_name : %s " % eastmoney_name)

            if eastmoney_name in stock_web.column_names:
                tmp_idx = stock_web.column_names.index(eastmoney_name)

                code_tmp = tmp_obj["code"]

                # 判断上海还是 深圳，东方财富 接口要求。

                if code_tmp.startswith("6"):
                    code_tmp = "SH" + code_tmp
                else:
                    code_tmp = "SZ" + code_tmp

                name_param = 'dailyline'
                tmp_url = WEB_EASTMONEY_URL % (
                    tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp,
                    kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"],
                    kind_table[name_param] + '_' + tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"])

                # print('tmp_url:')
                # print(tmp_url)
                tmp_obj["eastmoney_url"] = tmp_url
                logging.info(tmp_idx)
                logging.info(tmp_obj["eastmoney_url"])
                # logging.info(type(tmp_obj))
                # tmp.column_names.insert(tmp_idx, eastmoney_name)
        except Exception as e:
            print("error1 :", e)
    return stock_web_list

stock_web_list_process={
    'dailyline':process_dailyline,
    'indexline':process_index,
    'industryline':process_board,
    'etf_market':process_etf,
    'stock_sina_lhb_ggtj':process_stock_sina_lhb_ggtj,
    'stock_zh_ah_name':process_stock_zh_ah_name
}

def fun_none():
    print('wrong type')
    return None

# 获得股票数据内容。
class GetStockDataHandler(webBase.BaseHandler):
    def get(self):

        # 获得分页参数。
        start_param = self.get_argument("start", default=0, strip=False)
        length_param = self.get_argument("length", default=10, strip=False)
        print("page param:", length_param, start_param)

        name_param = self.get_argument("name", default=None, strip=False)

        type_param = self.get_argument("type", default=None, strip=False)

        stock_web = stock_web_dic.STOCK_WEB_DATA_MAP[name_param]
        print('name_param:',name_param)
        # https://datatables.net/manual/server-side
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        order_by_column = []
        order_by_dir = []
        # 支持多排序。使用shift+鼠标左键。
        for item, val in self.request.arguments.items():
            # logging.info("item: %s, val: %s" % (item, val) )
            if str(item).startswith("order["):
                print("order:", item, ",val:", val[0])
            if str(item).startswith("order[") and str(item).endswith("[column]"):
                order_by_column.append(int(val[0]))
            if str(item).startswith("order[") and str(item).endswith("[dir]"):
                order_by_dir.append(val[0].decode("utf-8"))  # bytes转换字符串

        search_by_column = []
        search_by_data = []

        # 返回search字段。
        for item, val in self.request.arguments.items():
            #logging.info("item: %s, val: %s" % (item, val))
            if str(item).startswith("columns[") and str(item).endswith("[search][value]"):
                logging.info("item: %s, val: %s" % (item, val))
                str_idx = item.replace("columns[", "").replace("][search][value]", "")
                int_idx = int(str_idx)
                # 找到字符串
                str_val = val[0].decode("utf-8")
                if str_val != "":  # 字符串。
                    search_by_column.append(stock_web.columns[int_idx])
                    search_by_data.append(val[0].decode("utf-8"))  # bytes转换字符串

        # 打印日志。
        search_sql = ""
        search_idx = 0
        logging.info(search_by_column)
        logging.info(search_by_data)
        for item in search_by_column:
            val = search_by_data[search_idx]
            logging.info("idx: %s, column: %s, value: %s " % (search_idx, item, val))
            # 查询sql
            if search_idx == 0:
                search_sql = " WHERE `%s` = '%s' " % (item, val)
            else:
                search_sql = search_sql + " AND `%s` = '%s' " % (item, val)
            search_idx = search_idx + 1

        # print("stockWeb :", stock_web)
        order_by_sql = ""
        # 增加排序。
        if len(order_by_column) != 0 and len(order_by_dir) != 0:
            order_by_sql = "  ORDER BY "
            idx = 0
            for key in order_by_column:
                # 找到排序字段和dir。
                col_tmp = stock_web.columns[key]
                dir_tmp = order_by_dir[idx]
                #print(col_tmp,':::',dir_tmp)
                if idx != 0:
                    order_by_sql += " ,cast(`%s` as decimal) %s" % (col_tmp, dir_tmp)
                else:
                    order_by_sql += " cast(`%s` as decimal) %s" % (col_tmp, dir_tmp)
                idx += 1
        # 查询数据库。
        limit_sql = ""
        if int(length_param) > 0:
            limit_sql = " LIMIT %s , %s " % (start_param, length_param)

        sql = " SELECT * FROM `%s` %s %s %s " % (
            stock_web.table_name, search_sql, order_by_sql, limit_sql)
        #sql += " WHERE `%s` = '%s' " % ('trade_date', date_now_str)
        count_sql = " SELECT count(1) as num FROM `%s` %s " % (stock_web.table_name, search_sql)

        logging.info("select sql : " + sql)
        logging.info("count sql : " + count_sql)
        stock_web_list = self.db.query(sql)

        stock_web_list = stock_web_list_process.get(name_param, fun_none)(stock_web_list,name_param,type_param,stock_web)
        '''
        for tmp_obj in (stock_web_list):

            if type_param == "editor":
                tmp_obj["DT_RowId"] = tmp_obj[stock_web.columns[0]]
            # logging.info(tmp_obj)
            try:
                # 增加columns 字段中的【东方财富】
                logging.info("eastmoney_name : %s " % eastmoney_name)

                if name_param=='dailyline':
                    tmp_obj['name']=stock_code_name[tmp_obj["code"]]

                if eastmoney_name in stock_web.column_names:
                    tmp_idx = stock_web.column_names.index(eastmoney_name)

                    code_tmp = tmp_obj["code"]

                    # 判断上海还是 深圳，东方财富 接口要求。
                    if kind_table[name_param]=='stock':
                        if code_tmp.startswith("6"):
                            code_tmp = "SH" + code_tmp
                        else:
                            code_tmp = "SZ" + code_tmp
                    elif kind_table[name_param]=='index':
                        code_tmp='zs'+code_tmp
                        #tmp_obj["code"]=code_tmp

                    if kind_table[name_param] == 'board':
                        tmp_url = WEB_EASTMONEY_BOARD_URL % (tmp_obj["code"], kind_table[name_param] + '_' + tmp_obj["code"], code_tmp, kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"])
                    else:
                        tmp_url = WEB_EASTMONEY_URL % (tmp_obj["code"], kind_table[name_param]+'_'+tmp_obj["code"], code_tmp, kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"],kind_table[name_param] + '_' + tmp_obj["code"])

                    #print('tmp_url:')
                    #print(tmp_url)
                    tmp_obj["eastmoney_url"] = tmp_url
                    logging.info(tmp_idx)
                    logging.info(tmp_obj["eastmoney_url"])
                    # logging.info(type(tmp_obj))
                    # tmp.column_names.insert(tmp_idx, eastmoney_name)
            except Exception as e:
                print("error1 :", e)
        '''
        stock_web_size = self.db.query(count_sql)
        logging.info("stockWebList size : %s " % stock_web_size)

        obj = {
            "draw": 0,
            "recordsTotal": stock_web_size[0]["num"],
            "recordsFiltered": stock_web_size[0]["num"],
            "data": stock_web_list
        }

        # logging.info("####################")
        #logging.info(obj)
        self.write(json.dumps(obj))
