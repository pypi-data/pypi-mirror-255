from decimal import Decimal

from horsetalk import RaceDesignation

from .future_form_factor import FutureFormFactor


class HandicapDebutBonus(FutureFormFactor):
    def _calc(self) -> Decimal:
        return Decimal(
            5
            if self.career.handicap_debut
            and self.conditions.race_designation == RaceDesignation.HANDICAP
            else 0
        )
