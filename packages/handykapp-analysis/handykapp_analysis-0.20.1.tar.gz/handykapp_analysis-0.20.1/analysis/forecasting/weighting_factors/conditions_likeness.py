from .weighting_factor import WeightingFactor


class ConditionsLikeness(WeightingFactor):
    def _calc(self) -> float:
        return float(self.current_conditions.like(self.past_conditions))
