from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from astrotoolz.core.enums import CoordinateSystem
from astrotoolz.core.objects.points import ASC, MC, MERCURY, MOON, VENUS
from astrotoolz.core.positions.base_position import BasePosition
from astrotoolz.core.positions.position_factory import create_position


def find_lon_increases(
    start_time: datetime,
    degrees: float,
    times: int,
    planets: List[str],
    coord_system: CoordinateSystem,
) -> Dict[str, List[Tuple[BasePosition, BasePosition]]]:
    lon_increases = {}

    for p in planets:
        lon_increases[p] = []

        bp = create_position(p, start_time, coord_system)

        for t in range(times):
            sq = _find_square_out(bp, degrees, _get_interval(p), coord_system)
            lon_increases[p].append((bp, sq))

            bp = sq

    return lon_increases


def generate_square_outs(
    start_time: datetime,
    degrees: float,
    planets: List[str],
    coord_system: CoordinateSystem,
) -> Dict[str, Tuple[BasePosition, BasePosition]]:
    square_outs = {}

    for p in planets:
        bp = create_position(p, start_time, coord_system)
        square_out = _find_square_out(bp, degrees, _get_interval(p), coord_system)
        square_outs[p] = (bp, square_out)

    return square_outs


def _find_square_out(
    starting_position: BasePosition,
    degrees: float,
    interval_hours: int,
    coord_system: CoordinateSystem,
) -> BasePosition:
    current_time = starting_position.dt
    cum_degrees = 0
    pp = starting_position

    while True:
        current_time += timedelta(hours=interval_hours)
        np = create_position(starting_position.point, current_time, coord_system)
        cum_degrees += abs(
            pp.speed.decimal * (interval_hours / 24)
        )  # should this really be abs? do we want to increase in case of retro too?
        if cum_degrees >= degrees:
            return pp

        pp = np


def _get_interval(planet: str) -> int:
    if planet in [ASC, MC, MOON, MERCURY, VENUS]:
        return 1
    else:
        return 24
