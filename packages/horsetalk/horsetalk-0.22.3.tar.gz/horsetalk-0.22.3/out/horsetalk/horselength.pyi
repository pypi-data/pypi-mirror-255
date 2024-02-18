from decimal import Decimal
from enum import Enum
from typing import Optional, Self

class Horselength(Decimal):
    class Description(Enum):
        DEAD_HEAT: int
        NOSE: float
        SHORT_HEAD: float
        HEAD: float
        SHORT_NECK: float
        NECK: float
        DISTANCE: int
        DHT = DEAD_HEAT
        NS = NOSE
        NSE = NOSE
        SHD = SHORT_HEAD
        HD = HEAD
        SNK = SHORT_NECK
        NK = NECK
        DIST = DISTANCE
        DST = DISTANCE
    def __new__(cls, value: Optional[float | Decimal | str] = None) -> Self: ...
    def __add__(self, other: Decimal | int) -> Horselength: ...
    def __radd__(self, other: Decimal | int) -> Horselength: ...
    def __sub__(self, other: Decimal | int) -> Horselength: ...
    def __rsub__(self, other: Decimal | int) -> Horselength: ...
