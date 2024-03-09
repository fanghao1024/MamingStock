import pandas as pd
import re


def get_all_stock_code_and_name():
    stock_catalog=pd.read_excel('../../data/stocks_code.xlsx',header=None)
    return stock_catalog