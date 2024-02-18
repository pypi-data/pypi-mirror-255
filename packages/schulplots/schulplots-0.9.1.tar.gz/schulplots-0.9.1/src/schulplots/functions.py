from dataclasses import dataclass, field
from typing import Optional, Any, Callable, Union, ClassVar, TYPE_CHECKING
from types import CodeType
from enum import Enum, unique

import numpy as np
from .converter import register_model, register_impl
try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

if TYPE_CHECKING:
    from .saxes import SAxes
from .utils.math_expression import MathExpression

@register_model
@dataclass
class SFunctionModel:
    class_id: ClassVar[str] = "Function"
    function: MathExpression
    name: str
    
@register_impl
class SFunction(SFunctionModel):
    def __init__(self, saxes: "SAxes", *args, **kwargs):
        self._saxes = saxes
        super().__init__(*args, **kwargs)
        f_x = lambda x: self.function.evaluate(dict(x=x), force_reeval=True)
        self._saxes.axes_functions.update({self.name: f_x})