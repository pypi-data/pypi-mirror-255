from horsetalk import Horse

from .race_performance import RacePerformance


class RaceResult(dict[Horse, RacePerformance]):
    def __init__(self, result: dict[Horse, RacePerformance]):
        super().__init__(sorted(result.items(), key=lambda x: x[1].outcome)[::-1])
