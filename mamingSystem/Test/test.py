import akshare as ak
import pandas as pd
pd.set_option('display.max_columns', 500)
index_zh_a_hist_df = ak.index_zh_a_hist(symbol="000016", period="daily", start_date="19700101", end_date="22220101")
print(index_zh_a_hist_df)
stock_zh_index_spot_df = ak.stock_zh_index_spot()
print(stock_zh_index_spot_df)
exit()

import akshare as ak
a=ak.fund_etf_fund_daily_em()
a.to_excel('etf.xlsx')
exit()

from bokeh.plotting import figure, show

x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')
p.line(x, y, legend_label="Temp.", line_width=2)
show(p)
exit()

import akshare as ak
stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
print(stock_board_industry_name_em_df)
exit()

#获取指数的成分股
import akshare as ak

index_stock_cons_df = ak.index_stock_cons(symbol="000300")
print(index_stock_cons_df)

exit()
#获取指数代码及名字
import akshare as ak

index_stock_info_df = ak.index_stock_info()
print(index_stock_info_df)

exit()




from pypnf import PointFigureChart
from pypnf import dataset

symbol = 'AAPL'  # or 'MSFT'

ts = dataset(symbol)

pnf = PointFigureChart(ts=ts, method='cl', reversal=2, boxsize=5, scaling='abs', title=symbol)

print(pnf)

#画水平线
import mplfinance as mpf
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2021-10-25", end="2021-10-29", interval='5m', progress=False)
df.index = pd.to_datetime(df.index)
df.index = df.index.tz_localize(None)

df = df[:200] # Limit data to emphasize the lines in the graph.

o_lines = []
m_lines = []
for c in df.columns[:4]:
    if c == 'Open':
        idx, price1, end, price2 = df[c].head(1).index[0], df[c].head(1)[0], df[c].tail(1).index[0], df[c].head(1)[0]
        o_lines.append((idx, price1))
        o_lines.append((end, price2))
    if c == 'High':
        idx, price1, end, price2 = df.loc[df[c].idxmax()].name, df.loc[df[c].idxmax()][c], df[c].tail(1).index[0], df.loc[df[c].idxmax()][c]
        m_lines.append((idx, price1))
        m_lines.append((end, price2))
        # print(m_lines)

mpf.plot(df, type='candle', alines=dict(alines=[o_lines, m_lines], colors=['b','r'], linewidths=2, alpha=0.4), style='yahoo')

