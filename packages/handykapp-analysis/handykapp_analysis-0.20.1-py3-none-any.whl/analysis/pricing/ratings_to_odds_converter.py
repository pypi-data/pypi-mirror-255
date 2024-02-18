from decimal import Decimal
from typing import List

from pybet import Odds  # type: ignore

from analysis.rating import FormRating


class RatingsToOddsConverter:
    @staticmethod
    def convert(ratings: List[FormRating], alpha: Decimal = Decimal(1)) -> List[Odds]:
        weightings = [alpha**rating for rating in ratings]
        total = sum(weightings)
        return [Odds.probability(weighting / total) for weighting in weightings]
