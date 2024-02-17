from typing import List

import numpy as np
import pandas as pd

from astrotoolz.core.angles.angle import Angle
from astrotoolz.tools.transit.transit import Transit
from astrotoolz.tools.transit.transit_table import TransitTable


def _generate_transit_str(transit: Transit, points_filter: List[str] = []):
    str = ""
    str += f"Name: {transit.natal_horoscope.name}"
    str += f"\nNatal Date and Time: {transit.natal_horoscope.dt}"
    str += f"\nTransit Date and Time: {transit.transit_horoscope.dt}"
    str += f"\nHouse System: {transit.natal_horoscope.house_system}"
    str += f"\nZodiac System: {transit.natal_horoscope.zodiac_system}"
    str += f"\nCoordinate System: {transit.natal_horoscope.coord_system}"
    str += "\n\nPoints:\n--------\n"
    str += "{:<10}{:<10}{:<10}{:<10}{:<10}".format(
        "Name", "Natal", "Transit", "Diff", "Transit house"
    )

    transit_points = {
        mp.base_position.point: mp for mp in transit.transit_horoscope.mgps
    }
    for point in transit.natal_horoscope.mgps:
        if point.base_position.point in points_filter:
            continue
        transit_point = transit_points[point.base_position.point]
        angle = Angle(
            point.base_position.dt, point.base_position, transit_point.base_position
        )
        str += f"\n{point.base_position.point:<10}{float_to_zodiacal(point.base_position.lon.decimal):<10}{float_to_zodiacal(transit_point.base_position.lon.decimal):<10}{round(angle.abs_diff,3):<10}{transit_point.house(transit.natal_horoscope.cusps):<10}"

    str += "\n---------------------\n\n\n"
    return str


def _generate_transit_table_str(transit_table: TransitTable):
    str = ""
    # Extract diff from Angle objects and create DataFrame
    planets = list(transit_table.angles.keys())
    matrix = np.empty((len(planets), len(planets)), dtype=object)
    for i, planet1 in enumerate(planets):
        for j, planet2 in enumerate(planets):
            # Find the corresponding Angle or Aspect object
            angle = next(
                (
                    angle
                    for angle in transit_table.angles[planet1]
                    if angle.target.point == planet2
                ),
                None,
            )
            matrix[i, j] = round(angle.abs_diff, 3) if angle else ""
    angles_df = pd.DataFrame(matrix, index=planets, columns=planets)
    str += "Angles:\n"
    str += "-------\n"
    str += angles_df.to_string()
    str += "\n"

    # Extract asp_diff from Aspect objects and create DataFrame
    matrix = np.empty((len(planets), len(planets)), dtype=object)
    for i, planet1 in enumerate(planets):
        for j, planet2 in enumerate(planets):
            # Find the corresponding Angle or Aspect object
            aspect = next(
                (
                    aspect
                    for aspect in transit_table.aspects[planet1]
                    if aspect.angle.target.point == planet2
                ),
                None,
            )
            matrix[i, j] = round(aspect.target_diff, 3) if aspect else ""
    aspects_df = pd.DataFrame(matrix, index=planets, columns=planets)
    str += "\nAspects:\n"
    str += "--------\n"
    str += aspects_df.to_string()

    # aspects in text
    str += "\n\nAspects:\n--------"
    for k, v in transit_table.aspects.items():
        str += f"\n{k}\n-------"
        for asp in v:
            str += f"\n{asp.angle.print_vedic_no_time()}, {asp.type}"
        str += "\n"

    str += "---------------------\n\n\n"

    return str


def print_transit_to_console(transit: Transit, points_filter: List[str] = []):
    transit_str = _generate_transit_str(transit, points_filter)
    transit_table_str = _generate_transit_table_str(transit.generate_transit_table())
    final_str = transit_str + "\n" + transit_table_str
    print(final_str)
