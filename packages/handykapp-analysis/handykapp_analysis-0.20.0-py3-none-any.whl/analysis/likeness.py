from typing import Callable, Self

from numpy import array, prod


class LikenessMixin:
    _likeness_functions: dict[str, Callable] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments

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


def discount(calculation: float) -> float:
    if calculation < 0:
        raise ValueError("Discount function must return a value below 1")
    return max(1 - calculation, 0)


def ignore(a: object, b: object) -> float:
    return 1


def likeness(a: LikenessMixin, b: LikenessMixin) -> float:
    return a.like(b)
