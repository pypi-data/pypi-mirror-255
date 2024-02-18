from dataclasses import dataclass
from typing import Union
import re

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from enum import Enum, auto
class FigAction(Enum):
    INTERACT = auto()
    SAVE = auto()

cm = 1./2.54 

size_re= re.compile(r"(-?[\d\.]+)(\s*)([a-z]+)")
units = {"cm": 1./2.54, 
         "mm": 0.1/2.54,
         "in": 1.}
#%%

class Size(float):
    def __new__(cls, value: Union[float, str]):
        if isinstance(value, str):
            if value.isnumeric():
                value = float(value)
            else:
                m = size_re.match(value)
                if m is None: 
                    raise ValueError("Invalid size")
                val, _, unit = m.groups()
                value = float(val) * units[unit]
        return float.__new__(cls, value)
    def __init__(self, value: Union[float, str]):
        self._init_as = str(value)
    def __repr__(self):
        return self._init_as
    __str__ = __repr__

@dataclass(frozen=True)
class Point:
    x: Size
    y: Size
    def args(self):
        return self.x, self.y
