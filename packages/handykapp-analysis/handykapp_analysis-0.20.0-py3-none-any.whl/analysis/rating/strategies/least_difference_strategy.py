from decimal import Decimal
from typing import List

from analysis.rating import FormRating

from .form_rating_level_setting_strategy import FormRatingLevelSettingStrategy


class LeastDifferenceStrategy(FormRatingLevelSettingStrategy):
    """
    A strategy for setting the level of a form rating.
    """

    def __init__(self, num_runners_to_use: int | None = None):
        """
        Initialize a LeastDifferenceStrategy instance.

        Args:
            num_runners_to_use: The number of runners to use in the calculation. If None, use all
                runners.
        """
        self.num = num_runners_to_use

    def _adjustment(self, priors: List[FormRating], raw: List[FormRating]) -> Decimal:
        """
        Calculate the adjustment to apply to the raw ratings.

        Args:
            priors: The prior assumptions about what the ratings should be.
            raw: The raw ratings.

        Returns:
            The adjustment to apply to the raw ratings.
        """
        useable_priors = priors[: self.num] if self.num else priors
        useable_raw = raw[: self.num] if self.num else raw
        ave_prior = sum(useable_priors) / len(useable_priors)
        ave_raw = sum(useable_raw) / len(useable_raw)
        return Decimal(ave_prior) - Decimal(ave_raw)
