from fast_tradier.models.ModelBase import ModelBase
from typing import List, Dict, Optional
from fast_tradier.models.trading.Sides import EquityOrderSide
from fast_tradier.models.trading.PriceTypes import EquityPriceType
from fast_tradier.models.trading.Duration import Duration
from fast_tradier.models.trading.OrderBase import OrderBase

class EquityOrder(OrderBase):
    def __init__(self, ticker: str, quantity: float, price: float, side: EquityOrderSide, price_type: EquityPriceType, duration: Duration, stop: Optional[float] = None) -> None:
        self.__ticker = ticker
        self.__quantity = quantity
        self.__price = price
        self.__side = side.value
        self.__price_type = price_type.value
        self.__duration = duration.value
        self.__stop = stop
        self.__status = None
        self.__order_class = 'equity'
        self.__id = None

    @property
    def ticker(self) -> str:
        return self.__ticker
    
    @property
    def quantity(self) -> float:
        return self.__quantity
    
    @quantity.setter
    def quantity(self, new_value: float):
        self.__quantity = new_value

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, new_value : float):
        self.__price = new_value

    @property
    def side(self) -> str:
        return self.__side

    @property
    def price_type(self) -> str:
        return self.__price_type

    @property
    def duration(self) -> str:
        return self.__duration

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, new_value: str):
        self.__status = new_value

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, new_value: int):
        self.__id = new_value

    @property
    def order_class(self) -> str:
        return self.__order_class

    @property
    def stop(self) -> Optional[float]:
        return self.__stop

    def __iter__(self):
        result = {
            "id": self.id,
            "status": self.status,
            "side": self.side,
            "symbol": self.ticker,
            "quantity": self.quantity,
            "duration": self.duration,
            "price": self.price,
            "type": self.price_type,
            "class": self.order_class,
            "stop": self.stop
        }

        yield from result.items()