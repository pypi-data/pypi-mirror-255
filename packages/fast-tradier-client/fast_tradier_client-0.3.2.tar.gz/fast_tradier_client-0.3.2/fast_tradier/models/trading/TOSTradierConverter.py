import re
from typing import Optional

tradier_option_symbol_pattern = re.compile(r'^([A-Z]+)([0-9]{2})([0-9]{4})(C|P)0?(\d+)0{3}')
class TOSTradierConverter(object):
    '''utility class for converting option symbols from Tradier to TOS or vice versa'''
    @staticmethod
    def tos_to_tradier(tos_option_symbol: str) -> Optional[str]:
        # e.g. SPXW230522C04210000
        tradier_option_format = '{ticker}{yy}{mmdd}{opt_type}{strike}000' # with padded 0s
        # e.g. SPXW_052523P1200
        tos_option_symbol_pattern = re.compile(r'^([A-Z]+)_([0-9]{4})([0-9]{2})(C|P)((\d)+)')
        # tradier_option_pattern = re.compile('^([A-Z]+)([2-9]{2})([0-9]{4})(C|P)0((\d)+)')

        d = re.search(tos_option_symbol_pattern, tos_option_symbol.upper())
        if d:
            ticker = d.group(1)
            mmdd = d.group(2)
            yy = d.group(3)
            option_type = d.group(4)
            strike = d.group(5)
            if len(strike) > 5:
                result = result[ : 5-len(strike)]
            elif len(strike) < 5:
                while len(strike) < 5:
                    strike = '0' + strike #prepend leading zeros to strike
                    result = tradier_option_format.format(ticker=ticker, yy=yy, mmdd=mmdd, opt_type=option_type, strike=strike)

            return result

        return tos_option_symbol

    @staticmethod
    def tradier_to_tos(tradier_option_symbol: str) -> str:
        d = re.search(tradier_option_symbol_pattern, tradier_option_symbol.upper())
        if d:
            ticker = d.group(1)
            yy = d.group(2)
            mmdd = d.group(3)
            opt_type = d.group(4)
            strike = d.group(5).lstrip('0') # remove leading zeroes
            tos_option_symbol = f'{ticker}_{mmdd}{yy}{opt_type}{strike}'
            return tos_option_symbol

        return tradier_option_symbol

    @staticmethod
    def get_strike(tradier_option_symbol: Optional[str]) -> Optional[float]:
        '''Parse out strike in float type from Tradier option symbol, could be None.'''
        if tradier_option_symbol is None:
            return None

        d = re.search(tradier_option_symbol_pattern, tradier_option_symbol.upper())
        if d:
            strike = d.group(5).lstrip('0') # remove leading zeroes
            try:
                return float(strike)
            except:
                return None