from typing import Any, Callable, List

import numpy as np
from events.astro_event import (
    DeclinationExtreme,
    ExtremeEvent,
    LatitudeExtreme,
    SpeedExtreme,
)
from scipy.signal import argrelextrema

from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition


def create_extreme_events(
    mps: List[MappedPosition], event_types: List[type]
) -> List[ExtremeEvent]:
    events = []
    for event_type in event_types:
        if not issubclass(event_type, ExtremeEvent):
            continue

        events += _create_events(
            _find_local_extrema(mps, _event_type_to_attribute(event_type), np.greater),
            event_type,
            "max",
        )

        events += _create_events(
            _find_local_extrema(mps, _event_type_to_attribute(event_type), np.less),
            event_type,
            "min",
        )
    return events


def _event_type_to_attribute(event_type) -> str:
    if event_type == DeclinationExtreme:
        return "dec"
    elif event_type == LatitudeExtreme:
        return "lat"
    elif event_type == SpeedExtreme:
        return "speed"


def _create_events(
    extremes: List[MappedPosition], event_type: type, type: str
) -> List[ExtremeEvent]:
    return [event_type(mp.dt, mp, type) for mp in extremes]


def _find_local_extrema(
    mapped_positions: List[MappedPosition],
    attribute: str,
    comparator: Callable[[Any, Any], bool],
) -> List[MappedPosition]:
    values = [getattr(mp.base_position, attribute) for mp in mapped_positions]
    values_array = np.array(values)
    extrema_indices = argrelextrema(values_array, comparator)
    extrema = [mapped_positions[i] for i in extrema_indices[0]]
    return extrema
