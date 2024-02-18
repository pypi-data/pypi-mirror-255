from decimal import Decimal
from typing import Self, Tuple, Type

import numpy as np
from horsetalk import Horselength


class BeatenDistances(tuple):
    """
    This class represents a tuple of horselength values used for calculating the distances between horses in a race.

    Args:
        value (tuple[int | float | Decimal | str]): A tuple containing the horselength values.

    Raises:
        TypeError: If an attempt is made to directly instantiate the BeatenDistances class.
        ValueError: If the first element of value is not None or 0 or if an invalid horselength value is encountered in value.

    Returns:
        An instance of the BeatenDistances class.
    """

    def __new__(cls: Type[Self], values: Tuple[int | float | Decimal | str]) -> Self:
        if cls == BeatenDistances:
            raise TypeError("BeatenDistances cannot be instantiated directly")

        if values[0] and int(values[0]) != 0:
            raise ValueError("First element of BeatenDistances must be None or 0")

        horselengths = []
        for v in values:
            hl = Horselength(v)
            if hl < 0:
                raise ValueError(f"Negative horselength value for BeatenDistances: {v}")
            horselengths.append(hl)

        return super().__new__(cls, horselengths)  # type: ignore


class CumulativeBeatenDistances(BeatenDistances):
    """
    This class represents a tuple of horselength values used for calculating the distances between horses in a race,
    where the values represent the cumulative beaten distances.

    Args:
        value (tuple[int | float | Decimal | str]): A tuple containing the horselength values.

    Raises:
        ValueError: If any item in value is less than the previous one or if the first element of value is not None or 0.

    Returns:
        An instance of the CumulativeBeatenDistances class.
    """

    def __new__(cls: Type[Self], values: Tuple[int | float | Decimal | str]) -> Self:
        horselengths = super().__new__(cls, values)  # type: ignore

        for i, v in enumerate(horselengths[1:]):
            if v < horselengths[i]:
                raise ValueError(
                    f"Invalid value at index {i + 1}: CumulativeBeatenDistances must increase monotonically"
                )

        return horselengths  # type: ignore

    def to_marginal(self) -> "MarginalBeatenDistances":
        """
        Convert the instance to a MarginalBeatenDistances instance.

        Returns:
            MarginalBeatenDistances: The instance converted to a MarginalBeatenDistances instance.
        """
        return MarginalBeatenDistances(np.diff(self, prepend=0))  # type: ignore


class MarginalBeatenDistances(BeatenDistances):
    """
    This class represents a tuple of horselength values used for calculating the distances between horses in a race,
    where the values represent the marginal beaten distances.

    Returns:
        An instance of the MarginalBeatenDistances class.
    """

    def to_cumulative(self) -> CumulativeBeatenDistances:
        """
        Convert the instance to a CumulativeBeatenDistances instance.

        Returns:
            CumulativeBeatenDistances: The instance converted to a CumulativeBeatenDistances instance.
        """
        return CumulativeBeatenDistances(np.cumsum(self))  # type: ignore
