from dataclasses import dataclass

from horsetalk import Draw, RaceWeight


@dataclass(frozen=True, kw_only=True)
class PerformanceContext:
    draw: Draw
    jockey: object
    weight_carried: RaceWeight
    weight_allowance: RaceWeight
