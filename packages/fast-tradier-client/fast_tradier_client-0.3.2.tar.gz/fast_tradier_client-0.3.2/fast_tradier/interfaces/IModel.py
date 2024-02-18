from typing import Dict
from interface import Interface

class IModel(Interface):
    def serialize(self) -> Dict:
        raise NotImplementedError('not implemented in interface')