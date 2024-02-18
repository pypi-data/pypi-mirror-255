from horsetalk import RaceDesignation

from analysis.rating import RacePerformance

from .race_conditions import RaceConditions


class RaceCareer(dict[RaceConditions, RacePerformance]):
    def __init__(self, race_career: dict[RaceConditions, RacePerformance]):
        super().__init__(sorted(race_career.items(), key=lambda x: x[0].datetime))

    @property
    def handicap_debut(self):
        return not any(
            race.race_designation == RaceDesignation.HANDICAP for race in self
        )

    @property
    def lto_win(self):
        return self.performances[-1].is_win

    @property
    def maiden(self):
        return not any(run.is_win for run in self.values())

    @property
    def unbeaten(self):
        return all(run.is_win for run in self.values())

    @property
    def performances(self):
        return list(self.values())
