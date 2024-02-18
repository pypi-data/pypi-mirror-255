from typing import Self

from horsetalk import RaceDistance as HorsetalkRaceDistance
from numpy import array, prod

from .likeness import discount


# TODO: Find a way to reimpliment LikenessMixin without it causing __new__ issues with the underlying Quantity class
class RaceDistance(HorsetalkRaceDistance):
    _likeness_functions = {
        "furlong": lambda a, b: discount((float(abs(a - b) / min(a, b)) / 1.5) ** 0.5)
    }

    def __getattr__(self, name):
        if name == "like":
            return self.like

        return super().__getattr__(name)

    def like(self, other: Self) -> float:
        likeness_base = float(bool(len(self._likeness_functions)) or self == other)

        factors = []
        for attribute, function in self._likeness_functions.items():
            try:
                a = getattr(self, attribute)
                b = getattr(other, attribute)
                factors.append(function(a, b))
            except Exception:
                raise ValueError(
                    f"Unable to calculate likeness: {attribute} comparison failed"
                )

        return prod(array([likeness_base, *factors]))
