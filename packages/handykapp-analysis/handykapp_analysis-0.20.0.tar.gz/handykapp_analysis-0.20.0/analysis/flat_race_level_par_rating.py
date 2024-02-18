from horsetalk import RaceLevel


class FlatRaceLevelParRating:
    _lookup = {
        "Group 1": 140,
        "Group 2": 130,
        "Group 3": 120,
        "Listed": 110,
        "Class 2": 100,
        "Class 3": 90,
        "Class 4": 80,
        "Class 5": 70,
        "Class 6": 60,
        "Class 7": 50,
    }

    @staticmethod
    def max(level: RaceLevel) -> int:
        if level.grade.racing_code.name == "NATIONAL_HUNT":
            raise ValueError("These race level pars are for flat racing only")
        return FlatRaceLevelParRating._lookup[str(level.grade) or str(level.class_)]

    @staticmethod
    def average(level: RaceLevel) -> int:
        return FlatRaceLevelParRating.max(level) - 35

    @staticmethod
    def min(level: RaceLevel) -> int:
        if level.grade.racing_code.name == "NATIONAL_HUNT":
            raise ValueError("These race level pars are for flat racing only")
        return FlatRaceLevelParRating.max(level) - 70
