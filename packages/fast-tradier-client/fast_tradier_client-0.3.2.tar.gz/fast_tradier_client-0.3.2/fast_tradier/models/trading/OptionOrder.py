from typing import Dict, List, Optional

from fast_tradier.models.trading.TOSTradierConverter import TOSTradierConverter
from fast_tradier.models.ModelBase import ModelBase
from fast_tradier.models.trading.Sides import OptionOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType
from fast_tradier.models.trading.Duration import Duration
from fast_tradier.models.trading.OrderBase import OrderBase

class OptionLeg(OrderBase):
    def __init__(self, underlying_symbol: str, option_symbol: str, side: OptionOrderSide, quantity: int, convert_tos_symbol: bool = True) -> None:
        self.__underlying_symbol = underlying_symbol
        self.__tos_option_symbol = TOSTradierConverter.tradier_to_tos(option_symbol) if convert_tos_symbol else option_symbol
        self.__option_symbol = TOSTradierConverter.tos_to_tradier(option_symbol) if convert_tos_symbol else option_symbol
        self.__side = side.value
        self.__quantity = quantity
        self.__convert_tos_symbol = convert_tos_symbol
        self.__strike: Optional[float] = TOSTradierConverter.get_strike(self.__option_symbol)

    @property
    def convert_tos_symbol(self) -> bool:
        return self.__convert_tos_symbol

    @property
    def underlying_symbol(self) -> str:
        return self.__underlying_symbol

    @property
    def option_symbol(self) -> str:
        return self.__option_symbol

    @property
    def tos_option_symbol(self) -> str:
        return self.__tos_option_symbol

    @property
    def side(self) -> str:
        return self.__side

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def strike(self) -> Optional[float]:
        return self.__strike

    # reverse open to close or vice versa
    def reverse_side(self) -> None:
        '''reverse option side: from sell_to_open to buy_to_close or buy_to_open to sell_to_close'''
        if self.__side == 'buy_to_open':
            self.__side = 'sell_to_close'
        elif self.__side == 'sell_to_open':
            self.__side = 'buy_to_close'
    
class OptionOrder(ModelBase):
    def __init__(self, ticker: str, price: float, price_type: OptionPriceType, duration: Duration, option_legs: List[OptionLeg]):
        if option_legs is None or len(option_legs) == 0:
            raise Exception('option_legs must contain at least 1 leg')

        self.__ticker = ticker
        self.__price = price
        self.__price_type = price_type.value
        self.__duration = duration.value
        self.__option_legs = option_legs
        self.__status = 'pending'
        self.__order_class = 'multileg' if len(option_legs) > 1 else 'option'
        self.__id = None

    @property
    def ticker(self) -> str:
        return self.__ticker

    @ticker.setter
    def ticker(self, new_value: str):
        self.__ticker = new_value

    @property
    def price(self) -> float:
        return self.__price

    @property
    def price_type(self) -> str:
        return self.__price_type

    @property
    def duration(self) -> str:
        return self.__duration
    
    @property
    def option_legs(self) -> List[OptionLeg]:
        return self.__option_legs

    @price.setter
    def price(self, new_value : float):
        self.__price = new_value

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
    
    def clone_option_legs(self, reverse_side: bool = False) -> List[OptionLeg]:
        '''deep clone option_legs'''
        cloned_legs = []
        for opt_leg in self.option_legs:
            leg = OptionLeg(
                underlying_symbol=opt_leg.option_symbol,
                option_symbol=opt_leg.option_symbol,
                side=OptionOrderSide(opt_leg.side),
                quantity=opt_leg.quantity,
                convert_tos_symbol=opt_leg.convert_tos_symbol)

            if reverse_side:
                leg.reverse_side()

            cloned_legs.append(leg)

        return cloned_legs
    
    def __iter__(self):
        '''for preparing to_json(), which will be sent to Tradier API to place option order'''
        result = {
            "id": self.id,
            "status": self.status,
            "symbol": self.ticker,
            "duration": self.duration,
            "price": self.price,
            "type": self.price_type,
            "class": self.order_class,
        }
        if len(self.option_legs) == 1:
            result['option_symbol'] = self.__option_legs[0].option_symbol
            result['tos_option_symbol'] = self.__option_legs[0].tos_option_symbol
            result['side'] = self.__option_legs[0].side
            result['quantity'] = self.__option_legs[0].quantity
        elif len(self.option_legs) > 1:
            for i in range(len(self.__option_legs)):
                opt_item = self.__option_legs[i]
                symbol_key = f'option_symbol[{i}]'
                result[symbol_key] = opt_item.option_symbol
                tos_symbol_key = f'tos_option_symbol[{i}]'
                result[tos_symbol_key] = opt_item.tos_option_symbol
                side_key = f'side[{i}]'
                result[side_key] = f'{opt_item.side}'
                quant_key = f'quantity[{i}]'
                result[quant_key] = f'{opt_item.quantity}'

        yield from result.items()