from datetime import datetime, timedelta
from typing import List

from astrotoolz.core.zodiac.positions.mapped_geo_position import MappedGeoPosition
from astrotoolz.tools.dasa.dasa import Dasa, DasaLevel

DASA_LENGTHS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

DASA_SEQUENCE = list(DASA_LENGTHS.keys())


DASA_TOTAL = 120


"""This calculation method gives +-1 days vs AstroSeek and has a 5-7 days difference vs Jagannatha Hora."""


def generate_dasas(
    moon_position: MappedGeoPosition, target_level: DasaLevel
) -> List[Dasa]:
    nakshatra = moon_position.vedic.nakshatra
    sidereal_lon = moon_position.vedic.lon
    progress = nakshatra.degree_range.progress(sidereal_lon.decimal)

    lord = nakshatra.ruler
    dasa_length = DASA_LENGTHS[lord]
    birth_date = moon_position.dt
    dasa_remaining = (1 - progress) * dasa_length
    dasa_elapsed = progress * dasa_length
    dasa_start = birth_date - timedelta(days=dasa_elapsed * 365.25)

    return calculate_dasa_periods(dasa_start, lord, target_level)


def calculate_dasa_periods(
    start_date: datetime,
    lord: str,
    target_level: DasaLevel,
) -> List[Dasa]:
    current_date = start_date
    dasas = []

    # Find the index of the starting Dasa
    starting_dasa_index = DASA_SEQUENCE.index(lord)

    # Calculate the remaining period for the starting Dasa
    end_date = current_date + timedelta(days=DASA_LENGTHS[lord] * 365.25)
    dasas.append(
        (
            Dasa(
                DasaLevel.MahaDasa,
                lord,
                current_date,
                end_date,
                calculate_sub_periods(
                    current_date,
                    end_date,
                    lord,
                    target_level,
                    DasaLevel.MahaDasa,
                ),
            )
        )
    )
    current_date = end_date

    # Loop through the Dasa sequence and calculate the periods
    for i in range(starting_dasa_index + 1, len(DASA_SEQUENCE) + starting_dasa_index):
        lord = DASA_SEQUENCE[i % len(DASA_SEQUENCE)]
        end_date = current_date + timedelta(days=DASA_LENGTHS[lord] * 365.25)
        sub_periods = calculate_sub_periods(
            current_date, end_date, lord, target_level, DasaLevel.MahaDasa
        )
        dasas.append(
            Dasa(DasaLevel.MahaDasa, lord, current_date, end_date, sub_periods)
        )

        current_date = end_date

    return dasas


def calculate_sub_periods(
    start_date: datetime,
    end_date: datetime,
    lord: str,
    target_level: DasaLevel,
    current_level: DasaLevel,
) -> List[Dasa]:
    if current_level == target_level:
        return []

    next = next_level(current_level)
    sub_periods = []
    total_days = (end_date - start_date).days
    # Reorder DASA_SEQUENCE starting with the lord
    lord_index = DASA_SEQUENCE.index(lord)
    reordered_sequence = DASA_SEQUENCE[lord_index:] + DASA_SEQUENCE[:lord_index]
    for sub_lord in reordered_sequence:
        sub_period_days = total_days * (DASA_LENGTHS[sub_lord] / 120)
        sub_end_date = start_date + timedelta(days=sub_period_days)

        sub_periods.append(
            Dasa(
                next,
                sub_lord,
                start_date,
                sub_end_date,
                calculate_sub_periods(
                    start_date,
                    sub_end_date,
                    sub_lord,
                    target_level,
                    next,
                ),
            )
        )
        start_date = sub_end_date

    return sub_periods


def next_level(level) -> DasaLevel:
    if level == DasaLevel.MahaDasa:
        return DasaLevel.Bhukti
    elif level == DasaLevel.Bhukti:
        return DasaLevel.Pratyantar
    elif level == DasaLevel.Pratyantar:
        return DasaLevel.Sookshma
    elif level == DasaLevel.Sookshma:
        return DasaLevel.Prana
