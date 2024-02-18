from typing import List

from pendulum.duration import Duration

from analysis.race_conditions import RaceConditions

from .race_performance import RacePerformance


class RateableResult:
    def __init__(
        self,
        conditions: RaceConditions,
        win_time: Duration,
        runs: List[RacePerformance],
    ):
        self.conditions = conditions
        self.win_time = win_time
        self.runs = runs
