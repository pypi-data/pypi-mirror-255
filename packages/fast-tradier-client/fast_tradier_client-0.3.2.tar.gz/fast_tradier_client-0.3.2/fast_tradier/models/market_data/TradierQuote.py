from typing import Dict, Tuple

from fast_tradier.models.ModelBase import ModelBase

class TradierQuote(ModelBase):
    def __init__(self, symbol: str, type: str, open: float, high: float, low: float, close: float, volume: float, bid: float, ask: float, last_price: float) -> None:
        self.__symbol = symbol
        self.__type = type #stock or option
        self.__open = open
        self.__high = high
        self.__low = low
        self.__close = close
        self.__volume = volume
        self.__bid = bid
        self.__ask = ask
        self.__mid = None if bid is None or ask is None else (bid + ask) / 2.0
        self.__last_price = last_price

    @property
    def ohlcv(self) -> Tuple:
        return self.__open, self.__high, self.__low, self.__close, self.__volume
    
    @property
    def quote_type(self) -> str:
        return self.__type

    @property
    def open_price(self) -> float:
        return self.__open

    @property
    def volume(self) -> float:
        return self.__volume

    @property
    def bid(self) -> float:
        return self.__bid

    @property
    def ask(self) -> float:
        return self.__ask

    @property
    def mid(self) -> float:
        return self.__mid

    @property
    def last_price(self) -> float:
        return self.__last_price

    @property
    def symbol(self) -> str:
        return self.__symbol

    def __iter__(self):
        yield from {
            "symbol": self.symbol,
            "type": self.quote_type,
            "open": self.open_price,
            "high": self.__high,
            "low": self.__low,
            "close": self.__close,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
            "last_price": self.last_price
        }.items()