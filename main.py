from datetime import datetime, timedelta

import pandas
from pykrx import stock
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_finance import candlestick2_ohlc
import mplfinance as mpf

market = 'KOSPI'  # KOSPI, KOSDAQ, KONEX 중 타깃 시장 지정 (StockInfo 클래스의 get_tickers 메소드에서 사용)

class StockInfo:
    def __init__(self):
        self.tickers: list = self.__get_tickers()
        self.firms: list = self.__get_firms(self.tickers)

    def __get_tickers(self):
        """
        조회 시점의 market 티커(종목코드)를 가져옵니다.
        :return: 조회 시점의 market 티커 리스트
        """
        today_ymd = datetime.today().strftime('%Y%m%d')
        tickers: list = stock.get_market_ticker_list(today_ymd, market=market)
        return tickers

    def __get_firms(self, tickers: list):
        """
        인자로 받은 종목 코드 리스트를 기반으로 기업명을 가져옵니다.
        :param tickers: 티커 리스트
        :return: 티커로 검색된 기업 리스트
        """
        firm_name_list: list = []
        for ticker in tickers:
            firm_name_list.append(stock.get_market_ticker_name(ticker))
        return firm_name_list

    def __search_firm(self, keyword: str):
        """
        검색어를 파라미터를 받아 검색어가 포함된 회사명을 리스트로 반환합니다.
        :param keyword: self.firms에서 검색하고자 하는 기업명
        :return: keyword가 포함된 회사명 리스트; 검색 결과가 없을 경우 False 반환
        """
        matching_results: list = [firm for firm in self.firms if keyword in firm]
        if len(matching_results) > 0:
            return matching_results
        else:
            return False

    def get_user_input(self):
        while True:
            temp_firms: list = []
            keyword_to_search: str = input('검색하고자 하는 기업의 이름을 입력하세요: ')
            if self.__search_firm(keyword_to_search):
                temp_firms = self.__search_firm(keyword_to_search)














