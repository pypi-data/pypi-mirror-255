import json
from dataclasses import dataclass
from typing import Dict, Optional, List

from fast_tradier.models.DataClassModelBase import DataClassModelBase

@dataclass
class Leg(DataClassModelBase):
    id: int
    type: str
    symbol: str
    side: str
    quantity: float
    status: str
    duration: str
    price: float
    avg_fill_price: float
    exec_quantity: float
    last_fill_price: float
    last_fill_quantity: float
    remaining_quantity: float
    create_date: str
    transaction_date: str
    # class: str
    class_type: str
    option_symbol: Optional[str]
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)
        if 'class' in api_resp_dict:
            self.class_type = api_resp_dict['class']

@dataclass
class AccountOrder(DataClassModelBase):
    id: int
    type: str
    symbol: str
    side: str
    quantity: float
    status: str
    duration: str
    price: float
    avg_fill_price: float
    exec_quantity: float
    last_fill_price: float
    last_fill_quantity: float
    remaining_quantity: float
    create_date: str
    transaction_date: str
    class_type: str
    num_legs: Optional[int]
    strategy: Optional[str]
    leg: Optional[List[Leg]]
    
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)
        for k, v in api_resp_dict.items():
            k_upper = k.upper()
            if k_upper == 'CLASS':
                self.class_type = v
            elif k_upper == 'LEG':
                self.leg = []
                for cur_leg in v:
                    self.leg.append(Leg(cur_leg))
            else:
                setattr(self, k, v)