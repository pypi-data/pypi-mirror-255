from enum import Enum

class EquityPriceType(Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"
    StopLimit = "stop_limit"

class OptionPriceType(Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"
    StopLimit = "stop_limit"
    
    Debit = "debit"
    Credit = "credit"
    Even = "even"