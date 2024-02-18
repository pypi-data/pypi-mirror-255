from dataclasses import dataclass
from typing import Dict, Optional

from fast_tradier.models.DataClassModelBase import DataClassModelBase

@dataclass
class Cash(DataClassModelBase):
    cash_available: float
    sweep: int
    unsettled_funds: float
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)

@dataclass
class Margin(DataClassModelBase):
    fed_call: int
    maintenance_call: int
    option_buying_power: float
    stock_buying_power: float
    stock_short_value: int
    sweep: int
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)

@dataclass
class Pdt(DataClassModelBase):
    fed_call: int
    maintenance_call: int
    option_buying_power: float
    stock_buying_power: float
    stock_short_value: int
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)

@dataclass
class AccountBalance(DataClassModelBase):
    option_short_value: int
    total_equity: float
    account_number: str
    account_type: str
    close_pl: float
    current_requirement: float
    equity: int
    long_market_value: float
    market_value: float
    open_pl: float
    option_long_value: float
    option_requirement: int
    pending_orders_count: int
    short_market_value: int
    stock_long_value: float
    total_cash: float
    uncleared_funds: int
    pending_cash: int
    margin: Optional[Margin]
    cash: Optional[Cash]
    pdt: Optional[Pdt]
    
    def __init__(self, api_resp_dict: Dict):
        self.__resp_dict = api_resp_dict
        self.margin = None
        self.cash = None
        self.pdt = None
        for k, v in api_resp_dict.items():
            key_upper = k.upper()
            if key_upper == 'MARGIN':
                self.margin = Margin(v)
            elif key_upper == 'CASH':
                self.cash = Cash(v)
            elif key_upper == 'PDT':
                self.pdt = Pdt(v)
            else:
                setattr(self, k, v)