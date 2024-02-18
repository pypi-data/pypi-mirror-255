from decimal import Decimal
from typing import Self


class Rating(Decimal):
    """
    A Decimal subclass that represents ratings. To be used as parent class.
    """

    solidity: Decimal

    def __new__(
        cls,
        value: float | Decimal | str,
        *,
        solidity: float | Decimal | str = 1,
    ) -> Self:
        """
        Creates a new Rating instance.

        Args:
            value: The value to create the Rating instance from.
            solidity: The solidity (i.e. reliability) of the rating on a scale from 0 to 1.

        Returns:
            A new Rating instance.
        """
        instance = super().__new__(cls, value)
        instance.solidity = Decimal(solidity)
        return instance
