from .weighting_factor import WeightingFactor


class RatingSolidity(WeightingFactor):
    def _calc(self) -> float:
        r = self.past_performance.form_rating
        return float(r.solidity if r is not None else 0)
