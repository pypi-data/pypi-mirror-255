from enum import Enum, auto


class NodeCalc(Enum):
    MEAN = "mean"
    TRUE = "true"

    @staticmethod
    def from_string(s: str):
        try:
            return NodeCalc[s.upper()]
        except KeyError:
            raise ValueError(f"'{s}' is not a valid NodeCalc")

    def swe_flag(self) -> str:
        return "MEAN_NODE" if self == NodeCalc.MEAN else "TRUE_NODE"

    def __str__(self):
        return self.name


class HouseSystem(Enum):
    PLACIDUS = auto()
    WHOLE_SIGN = auto()

    def __str__(self):
        return self.name


class Zodiac(Enum):
    TROPICAL = auto()
    SIDEREAL = auto()

    def __str__(self):
        return self.name


class CoordinateSystem(Enum):
    GEO = "geo"
    HELIO = "helio"

    @staticmethod
    def from_string(s: str):
        try:
            return CoordinateSystem[s.upper()]
        except KeyError:
            raise ValueError(f"'{s}' is not a valid CoordinateSystem")

    def __str__(self):
        return self.name


class AspectType(Enum):
    CONJUNCTION = 1
    OPPOSITION = 2
    SEXTILE = 3
    SQUARE = 4
    TRINE = 5
    QUINTILE = 6
    INCONJUNCT = 7

    def __str__(self):
        return self.name


class HoroscopeType(Enum):
    TROPICAL = auto()
    VEDIC = auto()
