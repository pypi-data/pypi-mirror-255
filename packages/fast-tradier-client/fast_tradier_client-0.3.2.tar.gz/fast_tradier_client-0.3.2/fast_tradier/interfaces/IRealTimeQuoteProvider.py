from interface import Interface
from typing import Optional

class IRealTimeQuoteProvider(Interface):
    '''interface for getting real time quote/price for a symbol'''
    def get_price(self, symbol: str) -> Optional[float]:
        raise NotImplementedError('not implemented in interface')