from horsetalk import Racecourse as HorsetalkRacecourse

from .likeness import LikenessMixin


def enum_likeness(step: float):
    return lambda a, b: max(
        a == b, 1 - step if any(x.value == 0 for x in [a, b]) else 1 - step * 2
    )


class Racecourse(LikenessMixin, HorsetalkRacecourse):
    """
    A class to represent a racecourse, wrapping the horsetalk class of the same name.

    """

    _likeness_functions = {
        "handedness": enum_likeness(0.1667),
        "contour": enum_likeness(0.1),
        "shape": enum_likeness(0.1),
        "style": enum_likeness(0.1),
        "surface": lambda a, b: max(
            a == b,
            0.83
            if all(x.name in ["FIBRESAND", "POLYTRACK", "TAPETA"] for x in [a, b])
            else 0.67,
        ),
    }
