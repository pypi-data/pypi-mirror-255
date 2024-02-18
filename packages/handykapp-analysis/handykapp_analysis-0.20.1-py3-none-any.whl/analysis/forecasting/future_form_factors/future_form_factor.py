from decimal import Decimal

from horsetalk import Horse

from analysis.race_career import RaceCareer
from analysis.race_conditions import RaceConditions


class FutureFormFactor:
    def __call__(
        self, horse: Horse, career: RaceCareer, conditions: RaceConditions
    ) -> Decimal:
        self.career = career
        self.conditions = conditions
        self.horse = horse
        return self._calc()

    def _calc(self) -> Decimal:
        raise NotImplementedError
