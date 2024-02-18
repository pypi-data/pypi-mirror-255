import os

from interface import implements
from typing import Optional
from autoscraper import AutoScraper
from pathlib import Path

from fast_tradier.interfaces.IRealTimeQuoteProvider import IRealTimeQuoteProvider

class YFinanceQuoteProvider(implements(IRealTimeQuoteProvider)):
    '''Fetch real time stock quote from Yahoo Finance using web scraper'''    
    def __init__(self, price_pattern_file_path: Optional[str] = None) -> None:
        if price_pattern_file_path is not None and not os.path.exists(price_pattern_file_path):
            raise FileNotFoundError(f'price pattern file {price_pattern_file_path} does not exist')
        default_price_pattern_file = Path(Path(__file__).resolve().parent, 'yahoo-price-pattern')
        self.__pattern_file_path = default_price_pattern_file if price_pattern_file_path is None else price_pattern_file_path
        self.__scraper = AutoScraper()
        self.__scraper.load(self.__pattern_file_path)
        self.__yfinance_base_url = 'https://finance.yahoo.com/quote/{symbol}'

    def get_price(self, symbol: str) -> Optional[float]:
        try:
            url = self.__yfinance_base_url.format(symbol = YFinanceQuoteProvider.convert_to_yf_ticker(symbol))
            result = self.__scraper.get_result_similar(url)
            quote_price = None
            if result is not None and len(result) > 0:
                quote_price = float(result[0])
            return quote_price
        except Exception as ex:
            return None

    @classmethod
    def convert_to_yf_ticker(cls, ticker: str):
        '''convert ticker/symbol to yahoo finance ticker'''
        ticker_yahoo_map = {
            'SPX' : '^GSPC',
            'SPXW' : '^GSPC',
            '$SPX.X' : '^GSPC',
            '$VIX.X' : '^VIX',
            'VIX' : '^VIX',
            'VVIX' : '^VVIX',
            'NDX' : '^NDX',
            }

        cur_ticker = ticker.upper()
        if cur_ticker in ticker_yahoo_map:
            return ticker_yahoo_map[cur_ticker]

        return ticker