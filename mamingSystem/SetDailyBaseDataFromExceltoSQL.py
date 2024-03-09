import pymysql
import os
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:@localhost:3308/stockdata')

dest_path='data/priceData'
pathDir =  os.listdir(dest_path)

db=pymysql.connect(host='localhost',port=3308,user='root',passwd='',database='stockdata',charset='utf8')
cur=db.cursor()
sql='TRUNCATE TABLE dailydata'
cur.execute(sql)
db.commit()

for filename in pathDir:
	file=os.path.join(dest_path,filename)
	daily_data=pd.read_excel(file)
	daily_data=daily_data.iloc[:,1:]
	daily_data.columns=['stock_code','trade_date','open','high','low','close','pre_close','price_change','pct_change','vol','deal_amount']
	print(daily_data)
	daily_data.to_sql(name='dailydata',con=engine,index=False, if_exists = 'append')

db.close()



