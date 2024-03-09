import sys,os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import akshare as ak
import gc


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
CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor,rc={'font.family':'SimHei'})

def fun_none():
    print('wrong type')
    return None

def PlotPnf(code,types,startday,endday):

    A=func_dist.get(types,fun_none)(code,startday,endday)
    A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    mpf.plot(A,type='pnf',style=CN,pnf_params=dict(box_size='atr',atr_length=10,reversal=2),mav=(5,10,20),volume=True,panel_ratios=(3,1),figscale=2,axtitle=types+code, scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
    plt.show()

def PlotPnf_Save(code,types,startday,endday):
    filename='../../Pnf/'+types+'/'+types+code+'.png'
    A=func_dist.get(types,fun_none)(code,startday,endday)
    A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    try:
        mpf.plot(A,type='pnf',style=CN,pnf_params=dict(box_size='atr',atr_length=10,reversal=2),mav=(5,10,20),volume=True,panel_ratios=(3,1),figscale=2,axtitle=types+code,savefig=filename, scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
        #plt.cla()
        plt.clf()
        plt.close('all')
    except Exception as ee:
        print(filename, 'is wrong:', ee)
    finally:
        del A
        gc.collect()
    #plt.show()

def PlotPnf_SaveAllIndex(startday,endday):
    stock_info_a_code_name_df = pd.read_excel('../data/index_code.xlsx', converters={u'code': str})
    mark = False
    types = 'index'
    lens=10
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        filename = '../../Pnf/' + types + '/' + types + code + name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if len(A)<lens:
            continue
        A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A,style=CN, type='pnf', pnf_params=dict(box_size='atr', atr_length=lens,reversal=2), mav=(5, 10, 20), volume=True,
                 panel_ratios=(4, 1), figscale=2, axtitle=types + code + '-'+name, savefig=dict(fname=filename,dpi=150,pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
            #plt.cla()
            #plt.clf()
            #plt.close('all')
        except Exception as ee:
            print(filename,'is wrong:',ee)
        #finally:
            #del A
            #gc.collect()
        # plt.show()

def PlotPnf_SaveAllETF(startday,endday):
    mark = False
    types = 'ETF'
    ETF_category = ak.fund_etf_category_sina()
    lens=10
    for code, name in zip(ETF_category.iloc[:, 0], ETF_category.iloc[:, 1]):
        print(code,name)
        if code=='sh501210' or code=='sh501086' or code=='sh501028':
            continue
        filename = '../../Pnf/' + types + '/' + types + code+name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if A is None:
            continue
        if len(A.index)==0 or len(A.index)<lens:
            continue
        A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='pnf', pnf_params=dict(box_size='atr', atr_length=lens,reversal=2), mav=(5, 10, 20), volume=True,
                 panel_ratios=(4, 1), figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=150, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
            #plt.cla()
            plt.clf()
            plt.close('all')
        except Exception as ee:
            print(filename,'is wrong:',ee)
        finally:
            del A
            gc.collect()
        # plt.show()

def PlotPnf_SaveAllBoard(startday,endday):
    mark = False
    types = 'board'

    stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

    lens=10
    for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
        print(code,name)
        filename = '../../Pnf/' + types + '/' + types + code+name + '.png'
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if len(A.index)<20:
            continue
        A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='pnf', pnf_params=dict(box_size='atr', atr_length=lens,reversal=2), mav=(5, 10, 20), volume=True,
                 panel_ratios=(4, 1), figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=150, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
            #plt.cla()
            plt.clf()
            plt.close('all')
        except Exception as ee:
            print(filename,'is wrong:',ee)
        finally:
            del A
            gc.collect()

def PlotPnf_SaveAllStock(startday,endday):
    types = 'stock'

    stock_info_a_code_name_df = ak.stock_info_a_code_name()

    mark = False
    lens=10
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        if mark == False and str(code) != '002601':
           continue
        else:
           mark = True

        filename = '../../Pnf/' + types + '/' + types + code+name + '.png'
        filename=filename.replace('*','')
        A = func_dist.get(types, fun_none)(code, startday, endday)
        if A is None:
            continue
        if len(A.index) == 0 or len(A.index) < 20:
            continue
        A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
        A.rename(columns={'date': 'datetime'}, inplace=True)
        A['datetime'] = pd.to_datetime(A['datetime'])
        A.set_index(['datetime'], inplace=True)
        try:
            mpf.plot(A, style=CN, type='pnf', pnf_params=dict(box_size='atr', atr_length=lens,reversal=2), mav=(5, 10, 20), volume=False,
                  figscale=2, axtitle=types + code + '-' + name,
                 savefig=dict(fname=filename, dpi=300, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
            plt.cla()
            plt.clf()
            plt.close('all')
        except Exception as ee:
            print(filename,'is wrong:',ee)
        finally:
            del A
            gc.collect()



#PlotPnf_SaveAllBoard('20100101','20220223')
#PlotPnf_SaveAllIndex('20100101','20220223')
PlotPnf_SaveAllStock('20100101','20220223')
#PlotPnf_SaveAllETF('20100101','20220218')


#PlotPnf_Save('399006','index','20120101','20220127')
