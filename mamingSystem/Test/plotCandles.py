import sys,os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

os.chdir(sys.path[0])
sys.path.append('../GetData/FromMySQL')
sys.path.append('../GetData/Tools')

import get_daily_index_market_from_mysql
import get_daily_industry_market_from_mysql
import get_daily_market_from_mysql
import get_daily_ETF_market_from_mysql

func_dist={'stock':get_daily_market_from_mysql.get_daily_market_bfq_from_dfcf,\
    'index':get_daily_index_market_from_mysql.get_daily_index_market_information,\
        'board':get_daily_industry_market_from_mysql.get_daily_industry_market_information,\
            'ETF':get_daily_ETF_market_from_mysql.get_ETF_daily_market_information}

def fun_none():
    print('wrong type')
    return None

def RSFactor(codeA,typeA,codeB,typeB,startday,endday):

    A=func_dist.get(typeA,fun_none)(codeA,startday,endday)
    B=func_dist.get(typeB,fun_none)(codeB,startday,endday)
    A.rename(columns={'open':'A_open','high':'A_high','low':'A_low','close':'A_close'},inplace=True)
    B.rename(columns={'open': 'B_open', 'high': 'B_high', 'low': 'B_low', 'close': 'B_close'}, inplace=True)

    A['trade_date'] = A['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    A.rename(columns={'trade_date': 'datetime'}, inplace=True)
    A['datetime'] = pd.to_datetime(A['datetime'])
    A.set_index(['datetime'], inplace=True)
    print(A)

    B['trade_date'] = B['trade_date'].apply(lambda x: x[0:4] + '-' + x[4:6] + '-' + x[6:])
    B.rename(columns={'trade_date': 'datetime'}, inplace=True)
    B['datetime'] = pd.to_datetime(B['datetime'])
    B.set_index(['datetime'], inplace=True)
    print(B)

    C=pd.merge(A,B,left_index=True,right_index=True)
    C['RS']=C['A_close']/C['B_close']
    #plt.plot(A['RS'])
    C=C[['RS']]
    print(C)
    A.rename(columns={'A_open':'open','A_high':'high', 'A_low':'low', 'A_close':'close'}, inplace=True)
    B.rename(columns={'B_open': 'open', 'B_high': 'high', 'B_low': 'low', 'B_close': 'close'}, inplace=True)
    mpf.plot(B,type='pnf')
    plt.show()
    mpf.plot(B,type='renko')
    plt.show()
    apds = [mpf.make_addplot(B,type='candle',panel=1,ylabel=typeB+codeB,mav=12),
            mpf.make_addplot(C,panel=2, type='line',color='g'),
            ]
    #涨红跌绿
    cncolors = mpf.make_marketcolors(up='r', down='g')
    CNs = mpf.make_mpf_style(marketcolors=cncolors)

    #所有其他颜色都和up与down一致
    mc = mpf.make_marketcolors(up='palegreen', down='c', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    # Create my own `marketcolors` to use with the `nightclouds` style:
    cncolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    CN = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=cncolor)

    mpf.plot(A, addplot=apds,style=CN,type='candle', panel_ratios=(1,1,1.2), figratio=(1, 1), figscale=2.5,ylabel=typeA+codeA)
    plt.show()
    return C

print(RSFactor('600519','stock','399006','index','20180101','20220101'))



'''
import mplfinance as mpf
import pandas as pd
import datetime
df = pd.DataFrame(ddata,index=pd.DatetimeIndex(times))

#实现画多图	
fig = mpf.figure(style='blueskies',figsize=(7,8))
ax1 = fig.add_subplot(2,1,1)
ax2 = ax1 #共用Y轴
#ax2 = ax1.twinx() #右边自己的Y轴
ax4 = fig.add_subplot(2,1,2)

ap =  mpf.make_addplot(df[['MA5','MA15','MA30','MA60']],ax=ax2,ylabel='MA')
#同时画MA，也用mplfinance自带的mav画ma，如果结果不一致，MA线应该有差异
mpf.plot(df, ax=ax1, mav=(5, 15, 30, 60), volume=ax4, addplot=ap, type='candle')
#mpf.plot(df, ax=ax1, volume=True, type='candle') #简单画法
fig.show()
'''