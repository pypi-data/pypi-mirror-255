from dataclasses import dataclass
from typing import Dict

from fast_tradier.models.DataClassModelBase import DataClassModelBase

@dataclass
class Position(DataClassModelBase):
    cost_basis: float
    date_acquired: str
    id: int
    quantity: float
    symbol: str
    
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)