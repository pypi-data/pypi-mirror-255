from typing import Any, Callable, Type

from horsetalk import RaceDistance, RaceWeight  # type: ignore
from pendulum.duration import Duration


class WeightPerLengthFormula:
    def __init__(
        self,
        input_type: Type[RaceDistance | Duration],
        formula: Callable[[Any], RaceWeight],
        weight_unit: str = "lb",
    ):
        self.input_type = input_type
        self.unit = weight_unit
        self._formula = formula

    def __call__(self, value: RaceDistance | Duration) -> RaceWeight:
        if not isinstance(value, self.input_type):
            raise TypeError(f"Expected {self.input_type}, got {type(value)}")
        return RaceWeight(**{self.unit: self._formula(value)})


BHA_GRAPH_LBS_PER_LENGTH = WeightPerLengthFormula(
    RaceDistance,
    lambda x: RaceWeight(
        lb={
            5: 3.4,
            6: 2.8,
            7: 2.4,
            8: 2.1,
            9: 1.9,
            10: 1.75,
            11: 1.6,
            12: 1.5,
            13: 1.4,
            14: 1.3,
            15: 1.2,
            16: 1.1,
            17: 1.075,
            18: 1.05,
            19: 1.025,
            20: 1,
        }[int(x.furlong)]
    ),
    weight_unit="lb",
)
