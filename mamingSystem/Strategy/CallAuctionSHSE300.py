import akshare as ak
import pandas as pd
stock_index_hist_df = ak.index_stock_hist(index="sh000001")
stock_index_hist_df.to_excel('sh000001.xlsx')
print(stock_index_hist_df)