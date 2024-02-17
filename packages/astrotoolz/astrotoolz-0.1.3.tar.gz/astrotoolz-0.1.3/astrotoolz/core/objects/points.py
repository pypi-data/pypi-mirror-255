from typing import Dict, List

from astrotoolz.core.enums import CoordinateSystem

MEAN_NODE = "MEAN_NODE"


EARTH = "earth"
MOON = "moon"
ASC = "asc"
MC = "mc"
SUN = "sun"
MOON = "moon"
MERCURY = "mercury"
VENUS = "venus"
MARS = "mars"
JUPITER = "jupiter"
SATURN = "saturn"
URANUS = "uranus"
NEPTUNE = "neptune"
PLUTO = "pluto"
NN = "north node"
SN = "south node"


PLANETS = [
    SUN,
    MOON,
    MERCURY,
    VENUS,
    MARS,
    JUPITER,
    SATURN,
    URANUS,
    NEPTUNE,
    PLUTO,
]

NODES = [NN, SN]

ANGULARS = [ASC, MC]

LUMINARIES = [SUN, MOON]


PLANETS_MAP = {
    "mercury": 1,
    "venus": 2,
    "mars": 3,
    "jupiter": 4,
    "saturn": 5,
    "uranus": 6,
    "neptune": 7,
    "pluto": 8,
}

ALL_POINTS = PLANETS + NODES
VEDIC_POINTS = [p for p in PLANETS if p not in ["uranus", "neptune", "pluto"]] + NODES

POINTS_NO_MOON = [p for p in PLANETS if p != MOON] + [NN]


def get_default_angle_targets(
    point: str, coordinate_system: CoordinateSystem
) -> List[str]:
    if point == SUN:
        return list(PLANETS_MAP.keys()) + (
            [NN] if coordinate_system == CoordinateSystem.GEO else []
        )
    elif point == MOON:
        return (
            list(PLANETS_MAP.keys())
            + [SUN]
            + ([NN] if coordinate_system == CoordinateSystem.GEO else [])
        )
    elif point == SN or point == NN:
        return []
    elif point in ANGULARS:
        return PLANETS + NODES
    else:
        return (
            [k for k, v in PLANETS_MAP.items() if v > PLANETS_MAP[point]] + [NN]
            if coordinate_system == CoordinateSystem.GEO
            else []
        )


def get_all_default_angle_targets(points: List[str]) -> Dict[str, List[str]]:
    targets = {}
    for p in points:
        targets[p] = [p for p in get_default_angle_targets(p) if p in points]
    return targets
