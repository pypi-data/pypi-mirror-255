from decimal import Decimal
from typing import Any

import numpy as np
from horsetalk import Horse

from analysis.flat_race_level_par_rating import FlatRaceLevelParRating
from analysis.forecasting.future_form_factors import (
    ExperienceImprovementBonus,
    HandicapDebutBonus,
    ThreeYearOldVsOlderBonus,
)
from analysis.forecasting.weighting_factors import ConditionsLikeness, RatingSolidity
from analysis.race_career import RaceCareer
from analysis.race_conditions import RaceConditions
from analysis.rating import FormRating
from analysis.rating.adjustments import EaseOfWinAdjustment


class FormPredictor:
    """
    A class for predicting form ratings for a race using current race conditions and past performance.
    """

    def __init__(
        self,
        horse: Horse,
        career: RaceCareer,
        conditions: RaceConditions,
    ):
        self.horse = horse
        self.career = career
        self.conditions = conditions

    @property
    def _ceiling(self) -> FormRating | None:
        """
        The ceiling of the past performances.

        Returns:
            The ceiling of the past performances.

        """
        if not len(self._rated_performances):
            return None

        top_performance = max(
            list(self._rated_performances), key=lambda x: x.form_rating
        )
        return (
            top_performance.form_rating
            if not (top_performance.is_win and len(self._rated_performances) <= 4)
            else None
        )

    @property
    def _additions(self) -> float:
        """
        Additions to make to form rating based on various potential improvements.

        Returns:
            Additions to make to form rating based on various potential improvements.

        """
        bonuses = [
            ExperienceImprovementBonus(),
            HandicapDebutBonus(),
            ThreeYearOldVsOlderBonus(),
        ]
        return float(sum(b(self.horse, self.career, self.conditions) for b in bonuses))

    @property
    def _floor(self) -> FormRating | None:
        """
        The floor of the past performances.

        Returns:
            The floor of the past performances.

        """
        if not len(self._rated_performances):
            return None

        worst_performance = min(
            list(self._rated_performances),
            key=lambda x: x.form_rating,
        )
        return r if (r := worst_performance.form_rating).solidity > 0 else None

    @property
    def _rated_performances(self) -> np.ndarray[float, np.dtype[Any]]:
        """
        A numpy array containing past performances that have been rated.

        Returns:
            A numpy array containing past performances that have been rated.
        """
        return np.array([p for p in self.career.performances if p and p.form_rating])

    @property
    def _ratings(self) -> np.ndarray[float, np.dtype[Any]]:
        """
        A numpy array containing the ratings of the past performances.

        Returns:
            A numpy array containing the ratings of the past performances.

        """
        return np.array([float(p.form_rating) for p in self._rated_performances])

    @property
    def _solidity(self) -> Decimal:
        """
        The solidity of the past performances.

        Returns:
            The solidity of the past performances.

        """
        return Decimal(str(min(sum(self._weightings), 1)))

    @property
    def _weightings(self) -> np.ndarray[float, np.dtype[Any]]:
        """
        A numpy array containing the weightings of the past performances.

        Returns:
            A numpy array containing the weightings of the past performances.

        """
        weightings = [RatingSolidity(), ConditionsLikeness()]
        return np.array(
            [
                np.prod(
                    np.array(
                        [
                            weighting(
                                self.horse,
                                past_conditions,
                                past_performance,
                                self.conditions,
                            )
                            for weighting in weightings
                        ]
                    )
                )
                for past_conditions, past_performance in self.career.items()
                if past_performance and past_performance.form_rating
            ]
        )

    def _weighted_percentile(
        self, percentile=5, zero_val=0, *, inverted=False
    ) -> np.ndarray[Any, Any]:
        """
        Calculate the weighted percentile of the past performances.

        Args:
            percentile (int, optional): The percentile to calculate. Defaults to 5.
            zero_val (int, optional): The value to use for the zeroth percentile. Defaults to 0.
            inverted (bool, optional): Whether to invert the ordering of the past performances. Defaults to False.

        Returns:
            np.ndarray[Any, Any]: The weighted percentile of the past performances.

        """
        indices = np.argsort(self._ratings)[:: -1 if inverted else 1]
        ordered_ratings = self._ratings[indices]
        ordered_weightings = self._weightings[indices]
        cum_percents = ordered_weightings.cumsum() / ordered_weightings.sum() * 100
        return np.interp(percentile, [0, *cum_percents], [zero_val, *ordered_ratings])

    def predict(self) -> FormRating | None:
        """
        Predict the expected FormRating for a horse, given past performances and current conditions

        Returns:
            FormRating: The predicted FormRating for the horse.
        """

        if not len(self._ratings):
            return FormRating(
                FlatRaceLevelParRating.average(self.conditions.race_level)
            )

        adjustment = EaseOfWinAdjustment()
        average = np.average(
            [float(p.form_rating + adjustment(p)) for p in self._rated_performances],
            weights=self._weightings,
        )  # type: ignore

        return FormRating(average + self._additions, solidity=self._solidity)

    def lower_bound(self):
        """
        Predict the lowest possible FormRating for a horse, given past performances and current conditions

        Args:
            min_val (int, optional): The minimum value to use for the zeroth percentile. Defaults to 0.

        Returns:
            FormRating: The lowest possible FormRating for the horse.
        """
        race_min_val = FlatRaceLevelParRating.min(self.conditions.race_level)

        if not len(self._ratings):
            return race_min_val * 1.25

        horse_min_val = (
            float(self._floor) + self._additions if self._floor else race_min_val
        )

        zero_value = float(race_min_val * (1 - self._solidity)) + (
            horse_min_val * float(self._solidity)
        )

        return (
            self._weighted_percentile(zero_val=zero_value)
            if self._floor
            else (0.05 * (min(self._ratings) - race_min_val) + race_min_val)
        )

    def upper_bound(self):
        """
        Predict the highest possible FormRating for a horse, given past performances and current conditions

        Args:
            max_val (int, optional): The maximum value to use for the zeroth percentile. Defaults to 140.

        Returns:
            FormRating: The highest possible FormRating for the horse.

        """
        race_max_val = FlatRaceLevelParRating.max(self.conditions.race_level)

        if not len(self._ratings):
            return race_max_val * 0.8

        horse_max_val = (
            float(self._ceiling) + self._additions if self._ceiling else race_max_val
        )

        zero_value = float(race_max_val * (1 - self._solidity)) + (
            horse_max_val * float(self._solidity)
        )
        return self._weighted_percentile(zero_val=zero_value, inverted=True)

    def to_debug(self):
        """
        Return a dictionary of the attributes of the FormPredictor for debugging purposes.

        Returns:
            dict: A dictionary of the attributes of the FormPredictor for debugging purposes.
        """
        return {
            "ceiling": self._ceiling,
            "additions": self._additions,
            "floor": self._floor,
            "ratings": self._ratings,
            "solidity": self._solidity,
            "performance_summary": [
                {
                    "course": conditions.racecourse.name,
                    "date": conditions.datetime.format("YYMMDD"),
                    "rating": performance.form_rating,
                    "likeness": float(self.conditions.like(conditions)),
                    "solidity": float(performance.form_rating.solidity),
                }
                for conditions, performance in self.career.items()
                if performance and performance.form_rating
            ],
        }
