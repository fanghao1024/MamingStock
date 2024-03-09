"""
从MySQL数据库里读取每日数据
输入：
	stock_code:	股票代码
	startdate:	统计起始日期，以20210412的八位字符串格式
	enddate:	统计结束日期，以20210412的八位字符串格式
返回：
	pandas.DataFrame格式
	trade_date
	stock_code
	成交时间
	成交价格
	价格变动
	成交量(手)
	成交额(元)
	性质
"""

import pymysql
from sqlalchemy import create_engine
import pandas as pd

pymysql.install_as_MySQLdb()


def get_the_balance_sheet_by_date(stock_code='000002', startdate='19901217', enddate='21000101'):
    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    # 定义要执行的SQL语句
    # sql = "select * from daily_market where stock_code="+stock_code+'and trade_date>='+startdate+' and trade_date<='+enddate
    # sql="select * from daily_market where stock_code="+stock_code
    # sql="select * from daily_market"
    sql = 'select * from the_balance_sheet where stock_code="{0}" and 报表日期 >="{1}" and 报表日期<="{2}"'.format(
        stock_code, startdate, enddate)
    df=pd.DataFrame()
    try:

        df = pd.read_sql(sql, con=db)

    except Exception as e:
        raise e
    finally:
        db.close()  # 关闭连接
        if len(df.index) != 0:
            return df
        else:
            return None

def get_the_balance_sheet_by_season(stock_code='000002', startyear='1990',startseason='1', endyear='2100',endseason='1'):
    db = pymysql.connect(host="localhost", port=3306, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    if startseason=='1':
        startday=startyear+'0331'
    elif startseason=='2':
        startday=startyear+'0630'
    elif startseason=='3':
        startday = startyear + '0930'
    elif startseason=='4':
        startday = startyear + '1231'

    if endseason=='1':
        endday=endyear+'0331'
    elif endseason=='2':
        endday=endyear+'0630'
    elif endseason=='3':
        endday = endyear + '0930'
    elif endseason=='4':
        endday = endyear + '1231'

    return get_the_balance_sheet_by_date(stock_code,startday,endday)


# get_the_balance_sheet_by_date('000001','20200101','20211231')
a = get_the_balance_sheet_by_season('000002')
print(a)
