from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, Mapping, Sequence, Tuple, Type, Union

__all__ = ["TPrimitive", "ChalkStructType"]


class ChalkStructType(type):
    __chalk_type_hints__: Dict[str, Type[TPrimitive]]

    def __new__(cls, name: str, bases: Tuple[Type], annotations: Dict[str, Type[TPrimitive]]):
        instance = super().__new__(cls, name, bases, annotations)
        instance.__chalk_type_hints__ = annotations
        return instance


TPrimitive = Union[
    None,
    str,
    int,
    float,
    bool,
    date,
    datetime,
    time,
    timedelta,
    Sequence["TPrimitive"],
    Mapping[str, "TPrimitive"],
    ChalkStructType,
]
