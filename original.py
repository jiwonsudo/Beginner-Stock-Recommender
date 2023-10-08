from datetime import datetime, timedelta

import pandas
from pykrx import stock
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_finance import candlestick2_ohlc

market = 'KOSPI'  # KOSPI, KOSDAQ, KONEX


class StockInfoHandler:
    def __init__(self):
        self.current_tickers: list = self.get_current_tickers()
        self.firms_df: pd.DataFrame = self.get_df_current_firms(self.current_tickers)
        self.get_user_firm_name_input()

    def get_user_firm_name_input(self):
        user_input = input('검색하려는 기업의 이름을 입력해주세요: ')
        # while True:
        #     try:
        #         searched_firms: list = self.search_firm_name_by_keyword(user_input)
        #     except Exception as error:
        #         print('에러발생', error)
        #         user_input = input('검색 결과가 없습니다. 다시 입력해주세요:')
        #     else:
        #         return searched_firms
        return self.search_firm_name_by_keyword(user_input)

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
        firm_name: str = stock.get_market_ticker_name(ticker)
        return firm_name

    def get_df_current_firms(self, tickers: list):
        """
        :return: list of current firm names, by using self.get_current_ticker and self.get_firm_name
        """
        current_firm_names: list = [self.get_firm_name(ticker) for ticker in tickers]

        data = {
            'firm_name': current_firm_names
        }

        df_current_firms: pd.DataFrame = pd.DataFrame(data, index=tickers)
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
        """
        :param keyword: keyword to search firms
        :return: tickers of firms searched, which contains keyword in its name.
        """
        searched_results: list = list(self.firms_df.index['firm_name'].str.contains(keyword))
        return searched_results

    def get_ticker_fundamental(self, ticker: str, before_date: str, period_unit: str):
        ticker_value_indicator = stock.get_market_fundamental()


class DataVisualizer(StockInfoHandler):
    def draw_ohlcv(self, ticker, ohlcv_df):
        date_list = []
        for date in ohlcv_df.index.tolist():
            date_list.append(str(date).replace('-', '')[2:8])

        # make data lists
        open_price_list = ohlcv_df.loc[:, ['시가']].values.flatten().tolist()
        close_price_list = ohlcv_df.loc[:, ['종가']].values.flatten().tolist()
        low_price_list = ohlcv_df.loc[:, ['저가']].values.flatten().tolist()
        high_price_list = ohlcv_df.loc[:, ['고가']].values.flatten().tolist()
        volume_list = ohlcv_df.loc[:, ['거래량']].values.flatten().tolist()

        # set initial figures
        fig = plt.figure(figsize=(10, 5))
        fig.set_facecolor('w')
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        axes = []
        axes.append(plt.subplot(gs[0]))
        axes.append(plt.subplot(gs[1], sharex=axes[0]))
        axes[0].get_xaxis().set_visible(False)

        ohlc = [open_price_list, high_price_list, low_price_list, close_price_list]

        # candlestick chart
        candlestick2_ohlc(axes[0], open_price_list, high_price_list, low_price_list, close_price_list, width=1,
                          colorup='r', colordown='b')
        axes[0].get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))  # thousand seperator

        # trading volume chart
        axes[1].bar(date_list, volume_list, color='k', width=0.6, align='center')
        axes[1].get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))  # thousand seperator

        # set other plt options
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:.0f}'.format(x) for x in current_values])
        fig.suptitle(f'{self.get_firm_name(ticker)} ({ticker})')
        plt.xlabel(f'조회기간: {date_list[0]}~{date_list[-1]}, 가격단위: 대한민국 원(KRW)')
        plt.xticks(rotation=60)
        plt.tight_layout()
        plt.show()

    # if __name__ == '__main__':
    while True:
        if input('주식 정보를 검색하시겠습니까? (y/n): ') != 'y':
            break
        else:
            while True:
                stock = StockInfoHandler()

# if __name__ == '__main__':
#     today_tickers = StockInfoHandler.get_current_tickers()
#     while True:
#         keyword : str = input('검색할 종목의 이름을 검색하세요: ')
#         firm_search_results = StockInfoHandler.search_firm_name_by_keyword(keyword)
#         if len(firm_search_results) > 1:
#             firm_names = map(lambda ticker: StockInfoHandler.get_firm_name(ticker), firm_search_results)
#             print(firm_names)
#             firm_ticker_to_search : str # ticker
#             while True:
#                 index_to_search = int(input('검색 결과가 많습니다. 결과들 중 검색할 회사의 순서 번호를 입력하세요: '))
#                 if (isinstance(index_to_search, int)):
#                     firm_ticker_to_search = firm_search_results[index_to_search + 1]
#                     break
#                 else: print('잘못된 입력값입니다.')
#         while True:
#             day_ago_to_search = input('검색 시작 범위 날짜를 입력하세요: ')
#             if isinstance(int(day_ago_to_search), int):
#                 break
#             else: print('잘못된 입력입니다.')
#
#         df_firm_search_result = StockInfoHandler.get_firm_ohlcv()
#         if isinstance(int(day_ago_to_search), int): # type check if day_ago_to_search is pure int
#             DataVisualizer.draw_ohlcv(firm_ticker_to_search, day_ago_to_search)
#             print(f'{StockInfoHandler.get_firm_name(firm_ticker_to_search)}의 그래프가 표시되었습니다.')
#             is_quit = input('프로그램을 중지하려면 "q" 또는 "Q"를, 계속하려면 아무 키나 누르십시오: ')
#             if is_quit == 'q' or is_quit == 'Q':
#                 break
