from __future__ import annotations
from interface import implements
from typing import Dict, Optional

from abc import abstractmethod
import json
import jsonpickle

from fast_tradier.interfaces.IModel import IModel

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.serialize()

class ModelBase(implements(IModel)):

    def __init__(self):
        raise NotImplementedError("ModelBase cannot be initiated")

    @abstractmethod
    def __iter__(self):
        '''method rquired for to_json() method. Optional if to_json() is not needed'''
        raise NotImplemented("__iter__() not implemented in ModelBase")

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)
    
    def __repr__(self) -> str:
        return self.__str__()

    def to_json(self) -> Dict:
        return json.loads(self.__str__())

    def serialize(self) -> Dict:
        '''serialize class object to json, which is parsable back to class object'''
        return jsonpickle.encode(self)

    @classmethod
    def deserialize_from_json(cls, json_obj) -> Optional[ModelBase]:
        '''Parse json object to class object. Could throw exception if not parsable'''
        return jsonpickle.decode(json_obj)