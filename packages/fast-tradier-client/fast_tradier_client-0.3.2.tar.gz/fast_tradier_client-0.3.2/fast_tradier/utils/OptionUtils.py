import pandas as pd
from typing import Tuple

OptionChain_Headers = ['symbol', 'strike', 'lastPrice', 'openInterest', 'ask', 'bid', 'expiration_date', 'bid_date', 'volume', 'underlying_price', 'updated_at', 'gamma', 'delta', 'vega']

class OptionUtils:
    @staticmethod
    def find_option_price(option_symbol: str, call_df: pd.DataFrame, put_df: pd.DataFrame) -> Tuple:
        '''find premium for the option_symbol, returns bid, ask and last price in tuple'''

        option_symbol = option_symbol.upper()
        iloc_idx_call = call_df.loc[call_df['symbol'] == option_symbol]
        iloc_idx_put = put_df.loc[put_df['symbol'] == option_symbol]
        target_idx = -1
        target_df = None
        result = (-1, -1, -1)

        if len(iloc_idx_call.index) > 0:
            target_idx = call_df.index.get_loc(iloc_idx_call.index[0])
            target_df = call_df
        elif len(iloc_idx_put.index) > 0:
            target_idx = put_df.index.get_loc(iloc_idx_put.index[0])
            target_df = put_df

        if target_df is not None:
            bid = target_df.iloc[target_idx]['bid']
            ask = target_df.iloc[target_idx]['ask']
            lastPrice = target_df.iloc[target_idx]['lastPrice']
            result = (bid, ask, lastPrice)
        return result