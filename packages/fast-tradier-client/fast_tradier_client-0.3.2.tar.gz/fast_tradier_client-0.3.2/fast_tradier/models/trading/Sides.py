from enum import Enum

class EquityOrderSide(Enum):
    Buy = "buy"
    BuyToCover = "buy_to_cover"
    Sell = "sell"
    SellShort = "sell_short"

class OptionOrderSide(Enum):
    BuyToOpen = "buy_to_open"
    BuyToClose = "buy_to_close"
    SellToOpen = "sell_to_open"
    SellToClose = "sell_to_close"