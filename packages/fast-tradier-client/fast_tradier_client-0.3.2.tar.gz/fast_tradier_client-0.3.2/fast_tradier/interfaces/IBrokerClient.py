import pandas as pd
from interface import implements, Interface
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

class IBrokerClient(Interface):

    def is_market_in_session_now(self) -> Tuple:
        raise NotImplementedError('not implemented in interface')
    
    def is_market_open_today(self, market: str='NYSE') -> Tuple:
        raise NotImplementedError('not implemented in interface')

    def get_quotes(self, symbols: List[str]):# -> List[Dict]:
        raise NotImplementedError('not implemented in interface')

    def get_history(self, symbol: str, start_date: date, end_date: date, interval: Interval = Interval.Daily, open_hours_only: bool = True) -> Optional[pd.DataFrame]:
        """Get history data for the given ticker symbol. start_date and end_date must be in date type.
        Returns a dataframe, with columns: open, high, low, close, volume. Index is their date.
        """
        raise NotImplemented('not implemented in interface')

    def get_order_status(self, order_id: int) -> Optional[str]:
        raise NotImplementedError('not implemented in interface')

    def get_option_expirations(self, symbol: str) -> List[str]:
        raise NotImplementedError('not implemented in interface')
    
    def place_order(self, order: OrderBase) -> Optional[int]:
        '''place order of any type: option or equity'''
        raise NotImplementedError('not implemented in interface')
    
    def place_option_order(self, order: OptionOrder) -> Optional[int]:
        raise NotImplementedError('not implemented in interface')

    def place_equity_order(self, order: EquityOrder) -> Optional[int]:
        raise NotImplementedError('not implemented in interface')
    
    def cancel_order(self, order_id: int) -> bool:
        raise NotImplementedError('not implemented in interface')
    
    def get_option_chain(self, symbol: str, expiration: str, greeks: bool = True) -> Optional[Dict]:
        raise NotImplementedError('not implemented in interface')

    def modify_option_order(self, modified_order: OptionOrder) -> bool:
        raise NotImplementedError('not implemented in interface')

    def get_positions(self) -> List[Position]:
        raise NotImplementedError('not implemented in interface')

    def get_account_balance(self) -> Optional[AccountBalance]:
        raise NotImplementedError('not implemented in interface')

    def get_account_orders(self) -> List[AccountOrder]:
        raise NotImplementedError('not implemented in interface')