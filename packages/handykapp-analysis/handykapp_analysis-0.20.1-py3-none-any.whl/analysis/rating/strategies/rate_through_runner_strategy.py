from decimal import Decimal
from typing import List

from analysis.rating import FormRating

from .form_rating_level_setting_strategy import FormRatingLevelSettingStrategy


class RateThroughRunnerStrategy(FormRatingLevelSettingStrategy):
    """
    A strategy for setting the level of a form rating.
    """

    def __init__(self, index: int = 0):
        """
        Initialize a RateThroughRunnerStrategy instance.

        Args:
            index: The index of the runner through which to rate the race.
        """
        self.index = index

    def _adjustment(self, priors: List[FormRating], raw: List[FormRating]) -> Decimal:
        """
        Calculate the adjustment to apply to the raw ratings.

        Args:
            priors: The prior assumptions about what the ratings should be.
            raw: The raw ratings.

        Returns:
            The adjustment to apply to the raw ratings.
        """
        return Decimal(priors[self.index] - raw[self.index])
