from dataclasses import dataclass
from typing import Dict

from fast_tradier.models.DataClassModelBase import DataClassModelBase

@dataclass
class Hlocv(DataClassModelBase):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)