from decimal import Decimal

from .future_form_factor import FutureFormFactor


class ExperienceImprovementBonus(FutureFormFactor):
    def _calc(self) -> Decimal:
        perfs = self.career.performances

        if not perfs:
            return Decimal(0)

        return Decimal(max(6 - len(perfs), 0) ** 3 / 10)
