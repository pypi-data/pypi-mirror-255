from itertools import groupby
from typing import List

from astrotoolz.core.angles.angle import Angle
from astrotoolz.core.enums import CoordinateSystem
from astrotoolz.core.events.aspects.aspect import Aspect
from astrotoolz.util.console_logger import ConsoleLogger

_logger = ConsoleLogger("AspectFactory")


def find_exact_aspects(
    angles: List[Angle],
    orb: float,
    aspects_include: List[int],
    coord_system: CoordinateSystem,
) -> List[Aspect]:
    # Find all aspects first
    all_aspects = find_aspects_list(angles, orb, aspects_include, coord_system)
    _logger.debug("All aspects found")

    # Group by date (year, month, day) first
    aspects_grouped_by_date = groupby(
        sorted(all_aspects, key=lambda asp: asp.angle.dt.date()),
        key=lambda asp: asp.angle.dt.date(),
    )
    _logger.debug("Grouped aspects by date")

    final_aspects = []

    # For each date group, group by asp_text
    for date, aspects_on_date in aspects_grouped_by_date:
        _logger.debug(f"Processing date group: {date}")
        aspects_grouped_by_asp_text = groupby(
            sorted(aspects_on_date, key=lambda asp: asp.asp_text),
            key=lambda asp: asp.asp_text,
        )

        # For each asp_text group, find the minimum by full datetime
        for asp_text, aspects_with_same_text in aspects_grouped_by_asp_text:
            _logger.debug(f"Processing asp_text group: {asp_text}")
            min_diff_asp = min(
                aspects_with_same_text,
                key=lambda asp: abs(asp.angle.abs_diff - asp.target_diff),
            )
            _logger.debug(
                f"Selected aspect with minimum difference to target diff: {min_diff_asp}"
            )
            final_aspects.append(min_diff_asp)

    _logger.debug("Completed processing all groups")
    return sorted(final_aspects, key=lambda asp: asp.angle.dt)


def find_aspects_list(
    angles: List[Angle],
    orb: float,
    aspects_include: List[int],
    coord_system: CoordinateSystem,
) -> List[Aspect]:
    aspects = []

    for angle in angles:
        negative = angle.abs_diff - orb
        positive = angle.abs_diff + orb
        for asp_value in aspects_include:
            if asp_value >= negative and asp_value <= positive:
                asp = Aspect(
                    angle.source.dt,
                    angle,
                    _get_asp_text(asp_value),
                    asp_value,
                    coord_system,
                )
                _logger.debug(f"Found aspect: {asp}")
                aspects.append(asp)

    return aspects


def _get_asp_text(asp_value: int) -> str:
    if asp_value in [0, 360]:
        return "conjunction"
    if asp_value in [30, 330]:
        return "semi-sextile"
    elif asp_value in [45, 315]:
        return "semi-square"
    elif asp_value in [60, 300]:
        return "sextile"
    elif asp_value in [90, 270]:
        return "square"
    elif asp_value in [120, 240]:
        return "trine"
    elif asp_value in [150, 210]:
        return "inconjunct"
    elif asp_value == 180:
        return "opposition"
    elif asp_value in [72, 144, 216, 288]:
        return "quintile"
    else:
        return ""
