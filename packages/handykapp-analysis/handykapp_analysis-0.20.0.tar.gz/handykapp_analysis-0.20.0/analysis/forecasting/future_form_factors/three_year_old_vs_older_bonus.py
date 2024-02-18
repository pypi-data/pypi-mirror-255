from decimal import Decimal

from .future_form_factor import FutureFormFactor


class ThreeYearOldVsOlderBonus(FutureFormFactor):
    def _calc(self) -> Decimal:
        return Decimal(10 if self.horse.age.official.years == 3 else 0)
