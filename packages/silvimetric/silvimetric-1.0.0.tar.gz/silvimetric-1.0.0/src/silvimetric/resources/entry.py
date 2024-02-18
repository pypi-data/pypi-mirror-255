import json
import numpy as np
import pdal
from typing import Self, Union
from abc import ABC, abstractmethod
from tiledb import Attr

class Entry(ABC):

    def __eq__(self, other: Self):
        return self.name == other.name and \
            self.dtype == other.dtype and \
            self.dependencies == other.dependencies

    @abstractmethod
    def entry_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def schema(self) -> Attr:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> object:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_string(data: str) -> Self:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class Attribute(Entry):

    def __init__(self, name: str, dtype: np.dtype, deps: list[Self]=None):
        super().__init__()
        self.name = name
        self.dtype = dtype
        self.dependencies = deps

    def entry_name(self) -> str:
        return self.name

    def schema(self) -> Attr:
        return Attr(name=self.name, dtype=self.dtype, var=True)

    def to_json(self) -> object:
        return {
            'name': self.name,
            'dtype': np.dtype(self.dtype).str,
            'dependencies': self.dependencies,
        }

    @staticmethod
    def from_string(data: Union[str, dict]) -> Self:
        if isinstance(data, str):
            j = json.loads(data)
        elif isinstance(data, dict):
            j = data
        else:
            raise TypeError(f'Type of data, {data} is not str or dict')
        name = j['name']
        dtype = j['dtype']
        deps = j['dependencies']
        return Attribute(name, dtype, deps)

    def __repr__(self):
        return json.dumps(self.to_json())

# A list of pdal dimensions can be found here https://pdal.io/en/2.6.0/dimensions.html
Pdal_Attributes = { d['name']: Attribute(d['name'], d['dtype']) for d in pdal.dimensions }
Attributes = Pdal_Attributes