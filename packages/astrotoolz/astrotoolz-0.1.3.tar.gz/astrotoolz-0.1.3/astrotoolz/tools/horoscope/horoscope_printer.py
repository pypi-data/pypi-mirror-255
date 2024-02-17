from typing import List

import pandas as pd

from astrotoolz.core.enums import HoroscopeType
from astrotoolz.core.events.aspects.aspect import Aspect
from astrotoolz.out.file import to_text_file
from astrotoolz.tools.horoscope.horoscope import Horoscope


def print_horoscope_to_console(
    horoscope: Horoscope,
    columns_filter: List[str] = [],
    points_filter: List[str] = [],
    aspects_filter: List[str] = [],
):
    print(_generate_str([horoscope], columns_filter, points_filter, aspects_filter))


def print_horoscopes_to_console(
    horoscopes: List[Horoscope],
    columns_filter: List[str] = [],
    points_filter: List[str] = [],
    aspects_filter: List[str] = [],
):
    print(_generate_str(horoscopes, columns_filter, points_filter, aspects_filter))


def print_horoscope_to_file(
    horoscope: Horoscope,
    filename: str,
    columns_filter: List[str] = [],
    points_filter: List[str] = [],
    aspects_filter: List[str] = [],
):
    to_text_file(
        _generate_str(
            filename, [horoscope], columns_filter, points_filter, aspects_filter
        )
    )


def print_horoscopes_to_file(
    horoscopes: List[Horoscope],
    filename: str,
    columns_filter: List[str] = [],
    points_filter: List[str] = [],
    aspects_filter: List[str] = [],
):
    to_text_file(
        filename,
        _generate_str(horoscopes, columns_filter, points_filter, aspects_filter),
    )


def _generate_str(
    horoscopes: List[Horoscope],
    columns_filter: List[str] = [],
    points_filter: List[str] = [],
    aspects_filter: List[str] = [],
):
    str = ""
    for horoscope in horoscopes:
        str += f"Name: {horoscope.config.name}"
        str += f"\nDate and Time: {horoscope.dt}"
        str += f"\nLongitude: {horoscope.config.lon}"
        str += f"\nLatitude: {horoscope.config.lat}"
        str += f"\nHouse System: {horoscope.config.house_system}"
        str += f"\nCoordinate System: {horoscope.config.coord_system}"
        str += "\n\nPoints:\n--------\n"
        # str += _get_headers(horoscope.config.type)()
        str += _get_values(horoscope.config.type)(
            horoscope, points_filter, columns_filter
        )

        str += "\n\nAspects:\n--------"
        for k, v in horoscope.aspects.items():
            if not bool(v) or k in aspects_filter:
                continue
            str += f"\n{k}\n-------"
            for asp in v:
                str += (
                    f"\n{_get_aspect_str(horoscope.config.type, asp)}, {asp.asp_type}"
                )
            str += "\n"

        str += "---------------------\n\n\n"
    return str


def _get_aspect_str(type: HoroscopeType, asp: Aspect):
    if type == HoroscopeType.TROPICAL:
        return asp.print_tropical_no_time()
    elif type == HoroscopeType.VEDIC:
        return asp.print_vedic_no_time()


def _get_values(type: HoroscopeType):
    if type == HoroscopeType.TROPICAL:
        return _get_tropical_values
    elif type == HoroscopeType.VEDIC:
        return _get_vedic_values


def _get_tropical_values(
    horoscope: Horoscope, points_filter: List[str] = [], columns_filter: List[str] = []
) -> str:
    all_columns = [
        "Name",
        "",
        "Position",
        "House",
        "Ruler",
        "Term",
        "Tarot",
        "Speed",
        "Phase",
        "Declination",
        "Latitude",
    ]

    data = []
    for mp in horoscope.mgps:
        if mp.point in points_filter:
            continue
        row = {
            "Name": mp.point,
            "": " R" if mp.retrograde else "",
            "Position": mp.tropical.position,
            "House": mp.tropical.house(horoscope.cusps),
            "Ruler": mp.tropical.sign_ruler,
            "Term": mp.tropical.term.name,
            "Tarot": mp.tropical.decan.name,
            "Speed": f"{mp.base_position.speed.str_decimal()} ({horoscope.get_daily_index(mp.point, 'speed')})",
            "Phase": f"{horoscope.phase(mp.point).str_decimal()} ({horoscope.get_daily_index(mp.point, 'phase')})",
            "Declination": f"{mp.base_position.dec.str_decimal()} ({horoscope.get_daily_index(mp.point, 'dec')})",
            "Latitude": f"{mp.base_position.lat.str_decimal()} ({horoscope.get_daily_index(mp.point, 'lat')})",
        }
        data.append(row)

    # Filter columns
    if columns_filter:
        all_columns = [col for col in all_columns if col not in columns_filter]

    df = pd.DataFrame(data, columns=all_columns)

    return df.to_string(index=False)


def _get_vedic_headers() -> str:
    return "{:<10}{:<3}{:<10}{:<10}{:<10}{:<20}{:<10}".format(
        "Name",
        "",
        "Position",
        "House",
        "Ruler",
        "Star",
        "Star Lord",
    )


def _get_vedic_values(horoscope: Horoscope, points_filter: List[str] = []) -> str:
    str = ""
    for mp in horoscope.mgps:
        if mp.point in points_filter:
            continue

        str += (
            f"\n{mp.point:<10}"
            f"{(' R' if mp.retrograde else ''):<3}"
            f"{mp.vedic.position:<10}"
            f"{mp.vedic.house(horoscope.cusps):<10}"
            f"{mp.vedic.sign_ruler:<10}"
            f"{mp.vedic.nakshatra.name:<20}"
            f"{mp.vedic.nakshatra_ruler:<10}"
        )
    return str
