from decimal import Decimal

from analysis.rating import RacePerformance


class RatingAdjustment:
    def __call__(self, performance: RacePerformance) -> Decimal:
        return Decimal("0")
