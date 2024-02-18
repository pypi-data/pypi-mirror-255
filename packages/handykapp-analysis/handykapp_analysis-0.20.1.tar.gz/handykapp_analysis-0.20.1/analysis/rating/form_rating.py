from decimal import Decimal
from typing import Self

from horsetalk import Horselength, RaceWeight  # type: ignore

from .rating import Rating


class FormRating(Rating):
    def adjust(self, delta: float | Decimal | str) -> Self:
        """
        Returns a new FormRating instance with the given delta added to the value.

        Args:
            delta: The delta to add to the value.

        Returns:
            A new FormRating instance.
        """
        return self.__class__(self + Decimal(delta), solidity=self.solidity)

    @classmethod
    def calculate(
        cls,
        *,
        beaten_distance: Horselength,
        weight_per_length: RaceWeight,
        weight_differential: RaceWeight = RaceWeight(lb=0),
        weight_for_age: RaceWeight = RaceWeight(lb=0),
        baseline: Decimal = Decimal(0),
    ) -> Self:
        """
        Calculates the FormRating for a horse from its beaten distance and a given weight per length

        Args:
            beaten_distance: The beaten distance to use in the calculation.
            weight_per_length: The weight per length to use in the calculation.
            weight_differential: The weight adjustment, e.g due to weight carried/jockey allowance, to use in the calculation.
            weight_for_age: The weight for age allowance to use in the calculation.
            baseline: The baseline rating to use in the calculation.

        Returns:
            The FormRating for the horse.
        """
        raw_delta = beaten_distance * Decimal(str(weight_per_length.lb))
        weight_adjustment = Decimal(str(weight_differential.lb)) + Decimal(
            str(weight_for_age.lb)
        )
        value = Decimal(str(round(float(baseline - raw_delta + weight_adjustment), 2)))
        solidity = 1 - (raw_delta.sqrt()) / 10
        return cls(value, solidity=solidity)
