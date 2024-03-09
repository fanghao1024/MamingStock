"""
按日期从MySQL数据库里读取特定'date'字段的全部记录
输入：
	date:	日期，以20210412的八位字符串格式
返回：
	pandas.DataFrame格式
	date
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
#pd.set_option('display.max_columns', 500)
pymysql.install_as_MySQLdb()


def get_stock_info_by_date(date='19901217'):
    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    # 定义要执行的SQL语句
    # sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
    # sql="select * from daily_market where stock_code="+stock_code
    # sql="select * from daily_market"
    sql = 'select * from daily_market where date={}'.format(date)
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

def get_stock_info_by_date_from_dfcf(date='19901217'):
    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    # 定义要执行的SQL语句
    # sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
    # sql="select * from daily_market where stock_code="+stock_code
    # sql="select * from daily_market"
    sql = 'select * from dailyline where date={}'.format(date)
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
#a = get_stock_info_by_date_from_dfcf('20210301')
#print(a)

