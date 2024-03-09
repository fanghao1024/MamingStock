import sys,os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import akshare as ak

#plt.switch_backend('cairo')
os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')

import get_daily_index_market_from_mysql
import get_daily_industry_market_from_mysql
import get_daily_market_from_mysql
import get_daily_ETF_market_from_mysql

func_dist={'stock':get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf,\
    'index':get_daily_index_market_from_mysql.get_daily_index_market_information,\
        'board':get_daily_industry_market_from_mysql.get_daily_board_market_bfq_from_dfcf,\
            'ETF':get_daily_ETF_market_from_mysql.get_ETF_daily_market_information}

cncolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
# Create a new style based on `nightclouds` but with my own `marketcolors`:
CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor,rc={'font.family':'SimHei'},mavcolors= ['#ef5714','#ef5714','#9f4878','#9f4878'])
lastday=''
def fun_none():
    print('wrong type')
    return None

def PlotRenko(code,types,startday,endday):

    A=func_dist.get(types,fun_none)(code,startday,endday)
    A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'trade_date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    mpf.plot(A,type='renko',style=CN,pnf_params=dict(box_size='atr',atr_length=10),mav=(5,10,20),volume=True,panel_ratios=(3,1),figscale=2,axtitle=types+code, scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
    plt.show()

def PlotRenko_Save(code,types,startday,endday):
    filename='../../Renko/'+types+'/'+types+code+'.png'
    A=func_dist.get(types,fun_none)(code,startday,endday)
    A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'trade_date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    mpf.plot(A,type='renko',style=CN,pnf_params=dict(box_size='atr',atr_length=10),mav=(5,10,20),volume=True,panel_ratios=(3,1),figscale=2,axtitle=types+code,savefig=dict(fname=filename, dpi=150, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
    #plt.show()

def PlotRenko_SaveAllIndex(startday,endday):
    stock_info_a_code_name_df = pd.read_excel('../data/index_code.xlsx', converters={u'code': str})
    mark = False
    types = 'index'
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        filename = '../../Renko/'+ types + '/' + types + code + name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'trade_date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A,style=CN, type='renko', pnf_params=dict(box_size='atr', atr_length=10), mav=(5, 10, 20), volume=True,
                 panel_ratios=(4, 1), figscale=2, axtitle=types + code + '-'+name, savefig=dict(fname=filename,dpi=150,pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
        except Exception as ee:
            print(filename,'is wrong:',ee)
        # plt.show()

def PlotRenko_SaveAllETF(startday,endday):
    mark = False
    types = 'ETF'
    ETF_category = ak.fund_etf_category_sina()
    lens=10
    for code, name in zip(ETF_category.iloc[:, 0], ETF_category.iloc[:, 1]):
        print(code,name)
        filename = '../../Renko/' + types + '/' + types + code+name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if A is None:
            continue
        if len(A.index)==0 or len(A.index)<lens:
            continue
        A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'trade_date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='renko', pnf_params=dict(box_size='atr', atr_length=lens), mav=(5, 10, 20), volume=True,
                  figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=150, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
        except Exception as ee:
            print(filename,'is wrong:',ee)
        # plt.show()

def PlotRenko_SaveAllBoard(startday,endday):
    mark = False
    types = 'board'

    stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

    mark = False
    lens=10
    for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
        print(code,name)
        filename = '../../Renko/' + types + '/' + types + code+name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if len(A.index) == 0 or len(A.index) < 20:
            continue
        A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'trade_date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='renko', pnf_params=dict(box_size='atr', atr_length=lens), mav=(5, 10, 20), volume=False,
                  figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=300, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
        except Exception as ee:
            print(filename,'is wrong:',ee)

def PlotRenko_SaveAllStock(startday,endday):
    types = 'stock'

    stock_info_a_code_name_df = ak.stock_info_a_code_name()

    mark = False
    lens=10
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        #if mark == False and str(code) != '300366':
        #    continue
        #else:
        #    mark = True

        filename = '../../Renko/'+ types + '/' + types + code+name + '.png'
        filename=filename.replace('*','')
        A = func_dist.get(types, fun_none)(code, startday, endday)

        if A is None:
            continue
        if len(A.index) < 5:
            continue
        A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'trade_date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='renko', pnf_params=dict(box_size='atr', atr_length=lens), mav=(5, 10, 20), volume=True,
                 figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=200, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
        except Exception as ee:
            print(filename,'is wrong:',ee)



#PlotRenko_SaveAllBoard('20120101','20220223')
PlotRenko_SaveAllIndex('20120101','20220223')
PlotRenko_SaveAllStock('20120101','20220223')
#PlotRenko_SaveAllETF('20120101','20220218')
