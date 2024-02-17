from typing import Callable, List, Optional

from astrotoolz.core.events.astro_event import (
    AstroEvent,
    DecanChange,
    DirectionChange,
    NakshatraChange,
    SiderealSignChange,
    TermChange,
    TropicalProgression,
    TropicalSignChange,
)
from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition as mp
from astrotoolz.util.common import find_smallest_elements, group_by, integral_ends_with

CheckFunction = Callable[[mp, mp], Optional[AstroEvent]]


def create_positional_events(
    mps: List[mp], event_types: List[type]
) -> List[AstroEvent]:
    if len(mps) < 2:
        return []

    check_functions = _get_check_functions(event_types)

    ret = []
    for i in range(1, len(mps)):
        ret += _check_changes(mps[i - 1], mps[i], check_functions)

    if event_types.__contains__(TropicalProgression):
        progs = _get_tropical_progressions(mps)
        ret += progs
    return ret


def _get_check_functions(
    event_types: List[type],
) -> List[CheckFunction]:
    check_functions = []

    for event_type in event_types:
        if not issubclass(event_type, AstroEvent):
            raise ValueError(f"{event_type.__name__} is not a subclass of AstroEvent")
        else:
            if event_type == DecanChange:
                check_functions.append(_check_decan_change)
            elif event_type == TropicalSignChange:
                check_functions.append(_check_tropical_sign_change)
            elif event_type == SiderealSignChange:
                check_functions.append(_check_vedic_sign_change)
            elif event_type == TermChange:
                check_functions.append(_check_term_change)
            elif event_type == NakshatraChange:
                check_functions.append(_check_nakshatra_change)
            elif event_type == DirectionChange:
                check_functions.append(_check_direction_change)
    return check_functions


def _check_changes(
    previous: mp,
    current: mp,
    check_functions: List[CheckFunction],
) -> List:
    ret = []
    for check_function in check_functions:
        event = check_function(previous, current)
        if event is not None:
            ret.append(event)
    return ret


def _check_decan_change(previous: mp, current: mp) -> Optional[DecanChange]:
    if previous.tropical.decan.id != current.tropical.decan.id:
        return DecanChange(current.dt, previous, current)


def _check_tropical_sign_change(
    previous: mp, current: mp
) -> Optional[TropicalSignChange]:
    if previous.tropical.sign.id != current.tropical.sign.id:
        return TropicalSignChange(current.dt, previous, current)


def _check_vedic_sign_change(previous: mp, current: mp) -> Optional[SiderealSignChange]:
    if previous.vedic.sign.id != current.vedic.sign.id:
        return SiderealSignChange(current.dt, previous, current)


def _check_term_change(previous: mp, current: mp) -> Optional[TermChange]:
    if previous.tropical.term.id != current.tropical.term.id:
        return TermChange(current.dt, previous, current)


def _check_direction_change(previous: mp, current: mp) -> Optional[DirectionChange]:
    if previous.direction != current.direction:
        return DirectionChange(current.dt, previous, current)


def _check_nakshatra_change(previous: mp, current: mp) -> Optional[NakshatraChange]:
    if previous.vedic.nakshatra.id != current.vedic.nakshatra.id:
        return NakshatraChange(current.dt, previous, current)


def _get_tropical_progressions(mps: List[mp]) -> List[AstroEvent]:
    events = []
    for mp in enumerate(mps):
        if integral_ends_with(5, mp.tropical.lon.decimal):
            events.append(TropicalProgression(mp.dt, mp, "50%"))
        elif integral_ends_with(7, mp.tropical.lon.decimal):
            events.append(TropicalProgression(mp.dt, mp, "70%"))
        elif integral_ends_with(3, mp.tropical.lon.decimal):
            events.append(TropicalProgression(mp.dt, mp, "30%"))

    groups = group_by(events, lambda x: int(x.mp.tropical.lon.decimal))

    closest = find_smallest_elements(groups, lambda x: x.mp.tropical.lon.decimal)

    filtered_closest = {
        k: v for k, v in closest.items() if str(v.mp.tropical.position).endswith("0")
    }
    return sorted(list(filtered_closest.values()), key=lambda x: x.mp.dt)
