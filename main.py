from datetime import datetime, timedelta
from pykrx import stock
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_finance import candlestick2_ohlc

market = 'KOSPI'  # KOSPI, KOSDAQ, KONEX

class StockInfoHandler:
    def get_current_tickers(self):
        """
        :returns: list of tickers, in type of list
        """
        today_ymd = datetime.today().strftime('%Y%m%d')
        tickers: list = stock.get_market_ticker_list(today_ymd, market=market)
        return tickers

    def get_firm_name(self, ticker: str):
        """
        :param ticker: ticker (stock code) for searching a firm
        :return: firm_name
        """
        firm_name : str = stock.get_market_ticker_name(ticker)
        return firm_name

    def get_df_current_firms(self):
        """
        :return: list of current firm names, by using self.get_current_ticker and self.get_firm_name
        """
        current_tickers = self.get_current_tickers()
        current_firm_names : list = [self.get_firm_name(ticker) for ticker in current_tickers]

        data = {
            'firm_name': current_firm_names
        }

        df_current_firms : pd.DataFrame = pd.DataFrame(data, index = current_tickers)
        return df_current_firms

    def get_firm_ohlcv(self, ticker: str, before_date: str, period_unit: str, frequency: str = 'd'):
        """
        :param ticker: firm's ticker to get data
        :param before_date: previous period to search from today
        :param period_unit: units from today to previous period (choose between 'd'(day) and 'w'(week))
        :param frequency: optional(default value: d(day))
        :return: ohclv(open, high, close, low, volume) data of firm; indicated by ticker
        """
        if period_unit == 'd':
            start_date = (datetime.now() - timedelta(days=int(before_date))).strftime('%Y%m%d')
        elif period_unit == 'w':
            start_date = (datetime.now() - timedelta(days=int(before_date))).strftime('%Y%m%d')
        today_ymd = datetime.now().strftime('%Y%m%d')
        end_date = today_ymd
        firm_ohlcv = stock.get_market_ohlcv(start_date, end_date, ticker, frequency)  # frequency: y, m, d
        return firm_ohlcv

    def search_firm_name_by_keyword(self, keyword: str):
        df_current_firms : pd.DataFrame = self.get_df_current_firms()
        searched_results: list = list(df_current_firms['firm_name'].str.contains(keyword))
        return searched_results

    def get_market_

class DataVisualizer:
    pass