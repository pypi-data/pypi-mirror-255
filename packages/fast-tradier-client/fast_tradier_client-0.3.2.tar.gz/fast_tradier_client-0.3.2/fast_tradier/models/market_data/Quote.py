from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

from fast_tradier.utils.TimeUtils import TimeUtils
from fast_tradier.models.DataClassModelBase import DataClassModelBase

@dataclass
class Quote(DataClassModelBase):
    symbol: str
    description: str
    exch: Optional[str]
    type: str
    last: Optional[float]
    change: Optional[float]
    volume: Optional[float]
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    bid: float
    ask: float
    underlying: str
    strike: Optional[float]
    change_percentage: Optional[float]
    average_volume: Optional[int]
    last_volume: Optional[int]
    trade_date: Optional[int]
    prevclose: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    bidsize: Optional[int]
    bidexch: Optional[str]
    bid_date: Optional[int]
    asksize: Optional[int]
    askexch: Optional[str]
    ask_date: Optional[int]
    open_interest: Optional[int]
    contract_size: Optional[int]
    expiration_date: Optional[str]
    expiration_type: Optional[str]
    option_type: Optional[str]
    root_symbol: str

    def __init__(self, api_resp_dict: Dict):
        super().__init__(api_resp_dict)

    @property
    def is_option(self) -> bool:
        return self.type.upper() == 'OPTION'

    @property
    def is_stock(self) -> bool:
        return self.type().upper() == 'STOCK'

    @property
    def trade_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.trade_date)

    @property
    def bid_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.bid_date)

    @property
    def ask_date_datetime(self) -> Optional[datetime]:
        return TimeUtils.convert_unix_ts(self.ask_date)