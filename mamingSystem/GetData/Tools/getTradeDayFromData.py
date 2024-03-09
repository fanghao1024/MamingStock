"""
从MySQL数据库里读取'trade_date'字段的全部不重复记录
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


def get_trade_day_from_data(startdate='19901217', enddate='21000101'):
    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    # 定义要执行的SQL语句
    # sql = "select * from daily_market where stock_code="+stock_code+'and trade_date>='+startdate+' and trade_date<='+enddate
    # sql="select * from daily_market where stock_code="+stock_code
    # sql="select * from daily_market"
    sql = 'select distinct trade_date from daily_market'
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


# get_daily_market_information('000001','20200101','20211231')
#a = get_trade_day_from_data('20210301', '20210301')
#a.to_excel('tradeDays.xlsx')
