import pendulum
from horsetalk import Horselength, RaceDistance, RaceWeight

from analysis.race_conditions import RaceConditions
from analysis.weight_for_age import (
    WeightForAgeConverter,
    WeightForAgeScale,
    WeightPerLengthFormula,
)

from .form_rating import FormRating
from .race_performance import RacePerformance
from .race_result import RaceResult


class FormRater:
    """
    A class for calculating form ratings for a race using cumulative beaten distances and selected other variables.

    Attributes:
        _weight_per_length_formula: The formula to calculate the weight equivalent of being beaten by a length.
        _weight_for_age_converter: The converter to adjust weights for horse age.

    Methods:
        rate(): Calculate the form ratings for each horse in a race.
    """

    def __init__(
        self,
        weight_per_length_formula: WeightPerLengthFormula = WeightPerLengthFormula(
            RaceDistance, lambda x: RaceWeight(lb=3)
        ),
        weight_for_age_converter: WeightForAgeConverter = WeightForAgeScale(),
    ):
        """
        Initialize a new FormRater instance.

        Args:
            **kwargs: Optional keyword arguments:
                weight_per_length_formula: The formula for converting distance to weight per length. Default returns RaceWeight(lb=3)
                weight_for_age_converter: The converter for calculating weight for age. Default returns RaceWeight(lb=0)
        """
        self._weight_per_length_formula = weight_per_length_formula
        self._weight_for_age_converter = weight_for_age_converter

    def rate(
        self, conditions: RaceConditions, result: RaceResult
    ) -> tuple[FormRating | None, ...]:
        """
        Calculate the form ratings for each horse in the race.

        Args:
            result: The result to be rated.

        Returns:
            Tuple[FormRating, ...]: A tuple of FormRating instances representing the ratings for each horse in the race.
        """
        winning_run = next(run for run in result.values() if run.is_win)
        base_weight = self._weight_differential(winning_run)

        input_type = self._weight_per_length_formula.input_type
        wpl = self._weight_per_length_formula(conditions.distance
            if input_type == RaceDistance
            else winning_run.time
            if winning_run and winning_run.time
            else pendulum.duration(minutes=2)
        )

        return tuple(
            FormRating.calculate(
                beaten_distance=Horselength(run.beaten_distance),
                weight_per_length=wpl,
                weight_differential=self._weight_differential(run, base_weight),
                weight_for_age=self._weight_for_age_converter.lookup(
                    conditions.distance, horse.age
                ),
            )
            for horse, run in result.items()
        )

    def _weight_differential(
        self, run: RacePerformance, base_weight: RaceWeight = RaceWeight(lb=0)
    ) -> RaceWeight:
        if not run.context:
            return RaceWeight(lb=0)

        lbs = (
            int(run.context.weight_carried.lb)
            + int(run.context.weight_allowance.lb)
            - int(base_weight.lb)
        )
        return RaceWeight(lb=lbs)
