import sys,os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import akshare as ak
#pd.set_option('display.max_columns', None)
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

# Create my own `marketcolors` to use with the `nightclouds` style:
cncolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
# Create a new style based on `nightclouds` but with my own `marketcolors`:
CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor, rc={'font.family': 'SimHei'},
                        mavcolors=['black', 'blue', 'red', 'yellow'])



def fun_none():
    print('wrong type')
    return None

def RSFactor(codeA,typeA,codeB,typeB,startday,endday):
    titlename=typeA+codeA+'_VS_'+typeB+codeB

    A=func_dist.get(typeA,fun_none)(codeA,startday,endday)
    B=func_dist.get(typeB,fun_none)(codeB,startday,endday)
    A.rename(columns={'open':'A_open','high':'A_high','low':'A_low','close':'A_close'},inplace=True)
    B.rename(columns={'open': 'B_open', 'high': 'B_high', 'low': 'B_low', 'close': 'B_close'}, inplace=True)

    A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)


    B['date'] = B['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    B.rename(columns={'date': 'datetime'}, inplace=True)
    B['datetime'] = pd.to_datetime(B['datetime'])
    B.set_index(['datetime'], inplace=True)

    C = pd.merge(A, B, left_index=True, right_index=True)
    # print(C)
    C['RS'] = C['A_close'] / C['B_close']

    C.dropna(axis=0, how='all')

    # plt.plot(A['RS'])
    C = C[['RS']]

    ROCPeriod = 10
    C = C[['RS']]
    C['ROC'] = C['RS'] - C['RS'].shift(ROCPeriod)
    # print(C)
    A.rename(columns={'A_open': 'open', 'A_high': 'high', 'A_low': 'low', 'A_close': 'close'}, inplace=True)
    B.rename(columns={'B_open': 'open', 'B_high': 'high', 'B_low': 'low', 'B_close': 'close'}, inplace=True)

    A = A.loc[C.index]
    B = B.loc[C.index]

    apds = [mpf.make_addplot(B,type='candle',panel=1,ylabel=typeB+codeB),
            mpf.make_addplot(C['RS'],panel=2, type='line',color='g',mav=(5,10,20)),
            mpf.make_addplot(C['ROC'], panel=3, type='line', color='g', mav=(5, 10, 20)),
            ]
    #涨红跌绿
    cncolors = mpf.make_marketcolors(up='r', down='g')
    CNs = mpf.make_mpf_style(marketcolors=cncolors)

    #所有其他颜色都和up与down一致
    mc = mpf.make_marketcolors(up='palegreen', down='c', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)


    mpf.plot(A, addplot=apds,style=CN,type='candle',axtitle=titlename, panel_ratios=(1,1,1.5,1.5), figratio=(1, 1), figscale=2.5,ylabel=typeA+codeA)
    plt.show()
    return C

def RSFactor_Save(codeA,typeA,codeB,typeB,startday,endday):
    file=typeA+codeA+'-'+typeB+codeB+'.png'
    filename = '../../RSFactor/' + file
    titlename = typeA + codeA + '_VS_' + typeB + codeB
    A=func_dist.get(typeA,fun_none)(codeA,startday,endday)
    if len(A)<=0:
        return
    B=func_dist.get(typeB,fun_none)(codeB,startday,endday)
    A.rename(columns={'open':'A_open','high':'A_high','low':'A_low','close':'A_close'},inplace=True)
    B.rename(columns={'open': 'B_open', 'high': 'B_high', 'low': 'B_low', 'close': 'B_close'}, inplace=True)

    A['date'] = A['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    #print(A)

    B['date'] = B['date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    B.rename(columns={'date': 'datetime'}, inplace=True)
    B['datetime'] = pd.to_datetime(B['datetime'])
    B.set_index(['datetime'], inplace=True)
    #print(B)

    C=pd.merge(A,B,left_index=True,right_index=True)

    C['RS']=C['A_close']/C['B_close']

    C.dropna(axis=0,how='all')

    #plt.plot(A['RS'])
    C=C[['RS']]

    ROCPeriod = 10
    C = C[['RS']]
    C['ROC'] = C['RS'] - C['RS'].shift(ROCPeriod)
    #print(C)
    A.rename(columns={'A_open':'open','A_high':'high', 'A_low':'low', 'A_close':'close'}, inplace=True)
    B.rename(columns={'B_open': 'open', 'B_high': 'high', 'B_low': 'low', 'B_close': 'close'}, inplace=True)

    A=A.loc[C.index]
    B=B.loc[C.index]

    apds = [mpf.make_addplot(B, type='candle', panel=1, ylabel=typeB + codeB),
            mpf.make_addplot(C['RS'], panel=2, type='line', color='g', mav=(5, 10, 20)),
            mpf.make_addplot(C['ROC'], panel=3, type='line', color='g', mav=(5, 10, 20)),
            ]
    #涨红跌绿
    cncolors = mpf.make_marketcolors(up='r', down='g')
    CNs = mpf.make_mpf_style(marketcolors=cncolors)

    try:
        mpf.plot(A, addplot=apds,style=CN,type='candle',axtitle=titlename,panel_ratios=(1,1,1.2,1.2), figratio=(1.5, 1), figscale=2.5,ylabel=typeA+codeA,savefig=dict(fname=filename, dpi=300, pad_inches=0.25), scale_padding={'left': 0.3, 'top': 0.3, 'right': 0.2, 'bottom': 0.3})
    except Exception as ee:
        print(filename, 'is wrong:', ee)

def board_VS_HS300(startday,endday):
    mark = False
    typeA = 'board'
    typeB = 'index'
    stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

    for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
        print(code, name)
        RSFactor_Save(code,typeA,'000300',typeB,startday,endday)

#以中证全指指数为基准
def board_VS_ZZQZ(startday,endday):
    mark = False
    typeA = 'board'
    typeB = 'index'
    stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})

    for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
        print(code, name)
        RSFactor_Save(code,typeA,'000985',typeB,startday,endday)

def ETF_VS_ZZQZ(startday,endday):
    mark = False
    typeA = 'ETF'
    typeB = 'index'
    stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})
    ETF_category = ak.fund_etf_category_sina()
    for code, name in zip(ETF_category.iloc[:, 0], ETF_category.iloc[:, 1]):
    #for code, name in zip(stock_info_a_code_name_df['bankuai_code'], stock_info_a_code_name_df['bankuai_name']):
        print(code, name)
        RSFactor_Save(code, typeA, '000985', typeB, startday, endday)

#以中证全指指数为基准
def Index_VS_ZZQZ(startday,endday):
    mark = False
    typeA = 'index'
    typeB = 'index'
    #stock_info_a_code_name_df = pd.read_excel('../data/hangye_dfcf.xlsx', converters={u'bankuai_code': str})
    stock_info_a_code_name_df = pd.read_excel('../data/index_code.xlsx', converters={u'code': str})
    for code, name in zip(stock_info_a_code_name_df['code'], stock_info_a_code_name_df['name']):
        print(code, name)
        RSFactor_Save(code,typeA,'000985',typeB,startday,endday)



board_VS_HS300('20180101','20220223')
board_VS_ZZQZ('20180101','20220223')
Index_VS_ZZQZ('20180101','20220223')
#ETF_VS_ZZQZ('20180101','20220221')
#RSFactor('600519','stock','399006','index','20180101','20220121')

