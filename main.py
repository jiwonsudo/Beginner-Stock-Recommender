from datetime import datetime, timedelta

from pykrx import stock
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_finance import candlestick2_ohlc

market = 'KOSPI'  # KOSPI, KOSDAQ, KONEX 중 타깃 시장 지정 (StockInfo 클래스의 get_tickers 메소드에서 사용)


class StockInfo:
    def __init__(self):
        print('프로그램 구동에 필요한 주식 정보를 불러오는 중입니다... 잠시만 기다려 주세요!')
        self.__tickers: list = self.__get_tickers()
        self.__firms: pd.DataFrame = self.__get_firms(self.__tickers)

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
        인자로 받은 티커 리스트를 기반으로 티커가 index인 기업명 데이터프레임을 가져옵니다.
        :param tickers: 티커 리스트
        :return: 티커로 인덱싱된 기업명 데이터프레임
        """
        firm_names_list: list = []
        for ticker in tickers:
            firm_names_list.append(stock.get_market_ticker_name(ticker))

        temp_firm_names = {
            'firm_name': firm_names_list
        }
        firm_names_df: pd.DataFrame = pd.DataFrame(temp_firm_names, index=tickers)

        return firm_names_df

    def _search_firm(self, keyword: str):
        """
        검색어를 파라미터로 받아 검색어가 포함된 회사의 티커를 리스트로 반환합니다.
        :param keyword: self.firms에서 검색하고자 하는 기업명
        :return: keyword가 포함된 회사명의 티커 리스트; 검색 결과가 없을 경우 False 반환
        """
        matching_results: list = list(self.__firms.index[self.__firms['firm_name'].str.contains(keyword)])  # self.__firms에서 검색어가 포함된 회사의 티커를 반환
        if len(matching_results) > 0:
            return matching_results
        else:
            return False

    def _get_firm_ohlcv(self, target_firm_ticker, before_date):
        """
        기업의 티커, 기간 전일을 파라미터로 받아 해당 기간 해당 기업의 ohlcv(open, high, low, close, value = 시작가, 고가, 저가, 종가, 거래량) 데이터를 DataFrame으로 반환합니다.
        :param target_firm_ticker: ohlcv 데이터를 조회할 기업의 티커
        :param before_date: 기업의 ohlcv 데이터를 조회할 오늘로부터 이전의 일수 (ex: 오늘이 9/20이고 before_date = 10이면, ohlcv 데이터는 9/10~9/20을 조회)
        :return: target_firm_ticker가 지칭하는 기업의 오늘로부터 before_date만큼 전의 날짜(단위: 일)의 기업 ohlcv 데이터
        """
        start_date = (datetime.now() - timedelta(days=int(before_date))).strftime('%Y%m%d')
        today_date = datetime.now().strftime('%Y%m%d')
        target_firm_ohlcv: pd.DataFrame = stock.get_market_ohlcv(start_date, today_date, target_firm_ticker)
        return target_firm_ohlcv

    def _get_ticker_fundamental(self, target_firm_ticker, date):
        """
        특정 종목의 티커를 이용, 특정 종목에 대해 조회 당일의 DIV/BPS/PER/EPS/PBR를 조회, 해당 정보가 담긴 데이터프레임을 반환합니다.
        :param target_firm_ticker: fundamental을 조회할 기업의 티커
        :return: 입력된 티커에 대해 조회한 DIV/BPS/PER/EPS/PBR 데이터가 담긴 데이터프레임
        """
        target_firm_fundamental: pd.DataFrame = stock.get_market_fundamental(date, date, target_firm_ticker)
        return target_firm_fundamental


class DataVisualizer:
    def _draw_ohlcv(self, ticker: str, ohlcv_df: pd.DataFrame):
        """
        기업의 ohlcv 데이터가 담긴 데이터프레임을 이용해 mpl_finance 라이브러리를 이용, candle stick chart(봉차트)를 그립니다.
        :param ticker: 차트를 그릴 기업의 티커 - 단, 그래프 제목 표시에만 사용됨 (데이터와 연관 x)
        :param ohlcv_df: 차트를 그릴 기업의 ohlcv 데이터가 담긴 데이터프레임
        :return: None (차트를 자체적으로 그림)
        """
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
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))  # 천 단위 콤마 구별

        # trading volume chart
        axes[1].bar(date_list, volume_list, color='k', width=0.6, align='center')
        axes[1].get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))  # 천 단위 콤마 구별

        # set other plt options
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:.0f}'.format(x) for x in current_values])
        fig.suptitle(f'{stock.get_market_ticker_name(ticker)} ({ticker})')
        plt.xlabel(f'조회기간: {date_list[0]}~{date_list[-1]}, 가격단위: 대한민국 원(KRW)')
        plt.xticks(rotation=60)
        plt.tight_layout()
        plt.show()


class StockInfoViewer(StockInfo, DataVisualizer):
    def __init__(self):
        super().__init__()
        self.ticker, self.ohlcv_data = self.__get_user_input()
        self.__show_stock_graph()
        self.__show_fundamental()

    def __get_user_input(self):
        """
        사용자의 입력을 받고, self.__search_firm 함수를 이용해 사용자가 검색을 원하는 하나의 기업의 티커와 주식 정보 데이터프레임을 반환합니다.
        :return: (사용자의 입력 중 최종적으로 선택한, 검색하고자 하는 기업의 티커), (self.__get_firm_ohlcv를 통해 얻은 before_date~오늘 간의 ohlcv 데이터프레임)
        """
        while True:
            keyword_to_search: str = input('검색하고자 하는 기업의 이름을 입력하세요: ')
            temp_firms_tickers = super()._search_firm(keyword_to_search)
            if temp_firms_tickers:  # 검색 결과 존재시
                while True:
                    temp_firms_names: list = [stock.get_market_ticker_name(ticker) for ticker in temp_firms_tickers]

                    if len(temp_firms_tickers) == 1:
                        break

                    # 정확히 일치하는 문자열이 있다면, 검색 결과 포함 확인 전에 while문 탈출
                    is_exact_match = False
                    for firm_name in temp_firms_names:
                        if keyword_to_search == firm_name:
                            is_exact_match = True
                            break
                    if is_exact_match: break

                    # 정확히 일치하는 문자열이 없을 경우 검색 결과들을 표시
                    print('검색 결과: ', *temp_firms_names)
                    keyword_to_search = input('검색 결과가 많습니다. 검색 결과 중 하나의 키워드를 입력하세요: ')

                    # 검색 결과에 입력 문자열이 포함되는지 확인 후 맞다면 재검색
                    if keyword_to_search in temp_firms_names:
                        temp_firms_tickers = super()._search_firm(keyword_to_search)
                        if len(temp_firms_tickers) == 1:
                            break
                    else:
                        print('검색 결과 중 하나의 기업명을 입력해 주세요.')
                print(f'{stock.get_market_ticker_name(temp_firms_tickers[0])}의 주가정보를 조회합니다.')
                while True:
                    date_input = input('조회하려는 기간의 날수(일 단위)를 입력하세요(ex: 30): ')
                    if date_input.isdigit():
                        before_date = int(date_input)
                        break
                    else:
                        print('잘못된 입력입니다. 다시 입력해 주세요.')
                return temp_firms_tickers[0], super()._get_firm_ohlcv(temp_firms_tickers[0], before_date)  # 기업 티커, 주식정보 데이터프레임을 묶은 튜플
            else:
                print('검색 결과가 없습니다. 다시 입력해 주세요.')

    def __show_stock_graph(self):
        super()._draw_ohlcv(self.ticker, self.ohlcv_data)
        start_date = str(self.ohlcv_data.index.tolist()[0]).replace('-', '')[2:8]
        end_date = str(self.ohlcv_data.index.tolist()[-1]).replace('-', '')[2:8]
        print(f'{stock.get_market_ticker_name(self.ticker)}의 {start_date}~{end_date}간 주가 정보가 표시되었습니다.')

    def __show_fundamental(self):
        print(f'{stock.get_market_ticker_name(self.ticker)}의 최근 영업일자 BPS/PER/PBR/EPS/DIV/DPS 조회정보는 아래와 같습니다.')
        print(super()._get_ticker_fundamental(self.ticker, str(self.ohlcv_data.index.tolist()[-1])))


StockInfoViewer()