from .going import Going as Going
from .race_designation import RaceDesignation as RaceDesignation
from .race_distance import RaceDistance as RaceDistance
from .race_level import RaceLevel as RaceLevel
from .racecourse import Racecourse as Racecourse
from .stalls_position import StallsPosition as StallsPosition
from dataclasses import dataclass
from pendulum import DateTime as DateTime

@dataclass(kw_only=True, frozen=True)
class RaceConditions:
    datetime: DateTime
    racecourse: Racecourse
    distance: RaceDistance
    going: Going
    race_designation: RaceDesignation
    race_level: RaceLevel
    stalls_position: StallsPosition | None = ...
    def __init__(self, *, datetime, racecourse, distance, going, race_designation, race_level, stalls_position) -> None: ...
