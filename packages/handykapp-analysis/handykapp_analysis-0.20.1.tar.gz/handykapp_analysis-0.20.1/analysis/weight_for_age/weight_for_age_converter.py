from collections import defaultdict
from decimal import Decimal
from typing import Dict, Self, Type

from horsetalk import HorseAge, RaceDistance, RaceWeight
from pendulum.datetime import DateTime


class WeightForAgeConverter(defaultdict):
    """
    The base class for all WeightForAgeConverter types, such as WeightForAgeScale and WeightForAgeTable.
    """

    def __init__(self, *, use_actual_age: bool = False) -> None:
        """
        Initialize a new instance of the WeightForAgeConverter class.
        """
        self.use_actual_age = use_actual_age
        super().__init__(lambda: defaultdict(int))

    def __new__(cls: Type[Self], *, use_actual_age: bool = False) -> Self:
        if cls == WeightForAgeConverter:
            raise TypeError("WeightForAgeConverter cannot be instantiated directly")

        return super().__new__(cls, use_actual_age)

    def add(self, distance: RaceDistance, values: Dict[range, int]) -> None:
        """
        Adds a new set of weight allowances for a given distance.

        Args:
            distance: A RaceDistance object representing a race distance in furlongs.
            values: A dictionary of weight allowances for a given age range.
        """
        self[distance.furlong] = values

    def lookup(
        self, distance: RaceDistance, age: HorseAge | int, date: DateTime | None = None
    ) -> RaceWeight:
        """
        Looks up a weight for the given age, distance, and date.

        Args:
            distance: A RaceDistance object representing the race distance in furlongs.
            horse_age: A HorseAge object representing the age of the horse being assessed.

        Returns:
            A Weight object representing the weight for age for the given horse's age at the given distance.
            If no weight is found, a default value of zero is given.
        """
        age = HorseAge(age, context_date=date) if isinstance(age, int) else age
        days = age.actual.days if self.use_actual_age else age.official.days

        if self[distance.furlong]:
            for key, val in self[distance.furlong].items():
                if days in key:
                    return RaceWeight(lb=self._process(key, val, days))
        return RaceWeight(lb=0)

    def _process(self, key: range, val: int, age_in_days: int) -> Decimal:
        """
        A lambda function that is used to calculate the weight allowance for a horse's age.

        Args:
            key: A range object representing the range of days for which the weight allowance is valid.
            val: An integer representing the weight allowance for the given range.
            age_in_days: An integer representing the age of the horse in days.

        Returns:
            An integer representing the weight allowance for the given horse's age.
        """
        raise NotImplementedError("Method must be implemented by subclass")
