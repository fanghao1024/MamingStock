"""
从MySQL数据库里读取每日数据
输入：
	startdate:	统计起始日期，以20210412的八位字符串格式
	enddate:	统计结束日期，以20210412的八位字符串格式
返回：
    date
	type:       总貌、主板、科创板
	item:       上市公司/家、总股本/亿股（份）、总市值/亿元、平均市盈率/倍、上市股票/只、流通股本/亿股（份）、流通市值/亿元
	number:     对映的数值

"""

import pymysql
from sqlalchemy import create_engine
import pandas as pd

pymysql.install_as_MySQLdb()


def get_sz_daily_summary_information(startdate='19901217', enddate='21000101'):
    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",
                         charset='utf8')
    # 定义要执行的SQL语句
    # sql = "select * from daily_market where stock_code="+stock_code+'and trade_date>='+startdate+' and trade_date<='+enddate
    # sql="select * from daily_market where stock_code="+stock_code
    # sql="select * from daily_market"
    sql = 'select * from sz_summary_data where 交易日期 >="{0}" and 交易日期<="{1}"'.format(startdate, enddate)
    df=pd.DataFrame()
    try:
        df = pd.read_sql(sql, con=db)
    except Exception as e:
        raise e
    finally:
        db.close()  # 关闭连接
        return df



# get_sz_daily_summary_information('000001','20200101','20211231')
#a = get_sz_daily_summary_information('20210317','20210317')
#a = get_sz_daily_summary_information()
#print(a)
