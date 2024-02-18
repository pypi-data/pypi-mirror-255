import pandas as pd
from interface import Interface
from typing import Tuple, List, Dict, Optional
from datetime import date

from fast_tradier.models.trading.OptionOrder import OptionOrder # order for placing
from fast_tradier.models.trading.EquityOrder import EquityOrder
from fast_tradier.models.account.AccountOrder import AccountOrder # retrieved from account
from fast_tradier.models.market_data.Quote import Quote
from fast_tradier.models.account.Position import Position
from fast_tradier.models.trading.Interval import Interval
from fast_tradier.models.account.AccountBalance import AccountBalance
from fast_tradier.models.trading.OrderBase import OrderBase

class IBrokerAsyncClient(Interface):

    async def is_market_in_session_now_async(self) -> Tuple:
        raise NotImplementedError('not implemented in interface')
    
    async def is_market_open_today_async(self, market: str='NYSE') -> Tuple:
        raise NotImplementedError('not implemented in interface')

    async def get_quotes_async(self, symbols: List[str]) -> List[Quote]:
        raise NotImplementedError('not implemented in interface')

    def get_history_async(self, symbol: str, start_date: date, end_date: date, interval: Interval = Interval.Daily, open_hours_only: bool = True) -> Optional[pd.DataFrame]:
        """Get history data for the given ticker symbol. start_date and end_date must be in date type.
        Returns a dataframe, with columns: open, high, low, close, volume. Index is their date.
        """
        raise NotImplemented('not implemented in interface')
    
    async def get_order_status_async(self, order_id: int) -> Optional[str]:
        raise NotImplementedError('not implemented in interface')
    
    async def get_option_expirations_async(self, symbol: str) -> List[str]:
        raise NotImplementedError('not implemented in interface')
    
    async def place_order_async(self, order: OrderBase) -> Optional[int]:
        '''place order of any type: option or equity'''
        raise NotImplementedError('not implemented in interface')

    async def place_option_order_async(self, order: OptionOrder) -> Optional[int]:
        raise NotImplementedError('not implemented in interface')
    
    async def place_equity_order_async(self, order: EquityOrder) -> Optional[int]:
        raise NotImplementedError('not implemented in interface')

    async def cancel_order_async(self, order_id: int) -> bool:
        raise NotImplementedError('not implemented in interface')

    async def get_option_chain_async(self, symbol: str, expiration: str, greeks: bool = True) -> Optional[Dict]:
        raise NotImplementedError('not implemented in interface')

    async def modify_option_order_async(self, modified_order: OptionOrder) -> bool:
        raise NotImplementedError('not implemented in interface')
    
    async def get_positions_async(self) -> List[Position]:
        raise NotImplementedError('not implemented in interface')
    
    async def get_account_balance_async(self) -> Optional[AccountBalance]:
        raise NotImplementedError('not implemented in interface')

    async def get_account_orders_async(self) -> List[AccountOrder]:
        raise NotImplementedError('not implemented in interface')