import re
from decimal import Decimal
from typing import Self

from .rating import Rating


class JockeyRating(Rating):
    @classmethod
    def parse(cls, string: str) -> Self:
        """
        Parses a string into a JockeyRating instance.

        Args:
            string: The string to parse.

        Returns:
            A new JockeyRating instance.
        """
        match = re.match(r"(\d+)(\**)", string)

        if not match:
            raise ValueError(f"Could not parse JockeyRating from '{string}'")

        number, stars = match.groups()
        return cls(number, solidity=Decimal(1 - len(stars) * 0.25))

    @property
    def delta(self) -> Decimal:
        """
        Returns the delta to an average jockey rating.

        Returns:
            The delta.
        """
        return Decimal(self - 10)
