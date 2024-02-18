from horsetalk import Horse

from analysis.race_conditions import RaceConditions
from analysis.rating import RacePerformance


class WeightingFactor:
    def __call__(
        self,
        horse: Horse,
        past_conditions: RaceConditions,
        past_performance: RacePerformance,
        current_conditions: RaceConditions,
    ) -> float:
        self.horse = horse
        self.past_conditions = past_conditions
        self.past_performance = past_performance
        self.current_conditions = current_conditions
        return self._calc()

    def _calc(self) -> float:
        raise NotImplementedError
