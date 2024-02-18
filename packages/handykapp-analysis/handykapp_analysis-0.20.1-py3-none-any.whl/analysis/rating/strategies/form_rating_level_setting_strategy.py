from decimal import Decimal
from typing import List

from analysis.rating import FormRating


class FormRatingLevelSettingStrategy:
    """
    A strategy for setting the level of a form rating.
    """

    def __call__(
        self, priors: List[FormRating], raw: List[FormRating]
    ) -> List[FormRating]:
        """
        Set the level of each form rating in the raw ratings based on the priors.

        Args:
            priors: The prior assumptions about what the ratings should be.
            raw: The raw ratings.

        Returns:
            The adjusted ratings.
        """
        if len(priors) != len(raw):
            raise ValueError("Priors and raw ratings must be the same length.")
        adjustment = self._adjustment(priors, raw)
        return [rating.adjust(adjustment) for rating in raw]

    def _adjustment(self, priors: List[FormRating], raw: List[FormRating]) -> Decimal:
        raise NotImplementedError
