import pymysql
from sqlalchemy import create_engine
import pandas as pd
pymysql.install_as_MySQLdb()

def get_daily_index_market_information(code='000001',startdate='19901217',enddate='21000101'):

    db = pymysql.connect(host="localhost", port=3308, user="root", passwd="88888888", database="stockdata",charset='utf8')

    # 定义要执行的SQL语句
    #sql = "select * from daily_market where stock_code="+stock_code+'and date>='+startdate+' and date<='+enddate
    #sql="select * from daily_market where stock_code="+stock_code
    #sql="select * from daily_market"
    sql='select * from indexline where code="{0}"'.format(code)
    try:

        df = pd.read_sql(sql, con=db)

    except Exception as e:
        raise e
    finally:
        db.close()  # 关闭连接
        if len(df.index)!=0:
            df = df[(df['date'] >= startdate)&(df['date'] <= enddate)]
            df = df.sort_values(by='date', ascending=True)
            return df
        else:
            return None

#print(get_daily_index_market_information('000001','20210101','20220101'))