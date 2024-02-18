from decimal import Decimal
from functools import reduce
from operator import mul

from horsetalk import Horse
from scipy.stats import rv_continuous

from analysis.forecasting import FormForecast
from analysis.forecasting.future_form_factors import FutureFormFactor
from analysis.forecasting.weighting_factors import WeightingFactor
from analysis.race_career import RaceCareer
from analysis.race_conditions import RaceConditions
from analysis.rating import FormRating
from analysis.rating.adjustments.rating_adjustment import RatingAdjustment


class FormForecastStrategy:
    def __call__(
        self, horse: Horse, career: RaceCareer, conditions: RaceConditions
    ) -> FormForecast:
        self.horse = horse
        self.career = career
        self.conditions = conditions
        self.adjustments: list[RatingAdjustment] = (
            [] if not hasattr(self, "adjustments") else self.adjustments
        )
        self.weighting_factors: list[WeightingFactor] = (
            [] if not hasattr(self, "weighting_factors") else self.weighting_factors
        )
        self.future_form_factors: list[FutureFormFactor] = (
            [] if not hasattr(self, "future_form_factors") else self.future_form_factors
        )

        return FormForecast(self._probability_distribution(), self._solidity())

    @property
    def _past_ratings(self) -> list[FormRating]:
        return [
            performance.form_rating.adjust(
                sum([adjustment(performance) for adjustment in self.adjustments])
            )
            for performance in self.career.values()
            if performance.form_rating
        ]

    @property
    def _weightings(self) -> list[float]:
        return [
            reduce(
                mul,
                [
                    factor(self.horse, past_conditions, past_rating, self.conditions)
                    for factor in self.weighting_factors
                ],
            )
            for past_conditions, past_rating in self.career.items()
        ]

    @property
    def _future_delta(self) -> Decimal:
        return sum(
            factor(self.horse, self.career, self.conditions)
            for factor in self.future_form_factors
        ) or Decimal("0")

    def _probability_distribution(self) -> rv_continuous:
        raise NotImplementedError

    def _solidity(self) -> Decimal:
        return Decimal("1")

    def using(
        self,
        *,
        adjustments: list[RatingAdjustment] = [],
        weighting_factors: list[WeightingFactor] = [],
        future_form_factors: list[FutureFormFactor] = [],
    ):
        self.adjustments = adjustments
        self.weighting_factors = weighting_factors
        self.future_form_factors = future_form_factors
        return self
