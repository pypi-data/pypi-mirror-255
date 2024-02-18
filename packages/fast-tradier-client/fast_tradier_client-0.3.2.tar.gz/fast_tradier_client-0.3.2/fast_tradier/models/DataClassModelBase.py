from typing import Dict
from dataclasses import dataclass
from fast_tradier.models.ModelBase import ModelBase

@dataclass
class DataClassModelBase(ModelBase):
    def __init__(self, api_resp_dict: Dict):
        if api_resp_dict is None:
            raise Exception("api_resp_dict is None")
        self.__resp_dict = api_resp_dict
        for k, v in api_resp_dict.items():
            setattr(self, k, v)
    
    def __iter__(self):
        yield from self.__resp_dict.items()