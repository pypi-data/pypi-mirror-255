from decimal import Decimal

from analysis.rating import RacePerformance
from analysis.rating.adjustments.rating_adjustment import RatingAdjustment


class EaseOfWinAdjustment(RatingAdjustment):
    def __init__(self, *, lbs_per_length: Decimal = Decimal("4")):
        self.lbs_per_length = lbs_per_length

    def __call__(self, performance: RacePerformance) -> Decimal:
        if not performance.is_win:
            return Decimal("0")

        bonus_words = ["readily", "easily", "comfortably", "impressive"]

        lengths_ahead = Decimal(abs(min(0, float(performance.beaten_distance or "0"))))
        ease_bonus = Decimal(
            "1.5"
            if performance.comments
            and any(
                word in performance.comments.lower().split(" ") for word in bonus_words
            )
            else "1"
        )

        return lengths_ahead * (self.lbs_per_length ** Decimal("0.5")) * ease_bonus
