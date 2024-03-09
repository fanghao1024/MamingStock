

import datetime

#生成当天日期，例如‘20210317’的形式
today=datetime.date.today()
today=today.strftime('%Y%m%d')

#生成上证的综合概况
import GetData.ToMySQL.get_sh_daily_summary
GetData.ToMySQL.get_sh_daily_summary.get_sh_daily_summary_mysql()

#生成深证的综合概况
import GetData.ToMySQL.get_sz_daily_summary
GetData.ToMySQL.get_sz_daily_summary.get_sz_period_summary(today,today)
'''
import GetData.get_daily_market
GetData.get_daily_market.get_daily_market_price(today,today)

import GetData.get_daily_deal
GetData.get_daily_deal.get_daily_deal_information(today,today)
'''