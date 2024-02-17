from typing import Dict, List, Type

from astrotoolz.core.angles.angle import Angle
from astrotoolz.core.angles.angle_factory import generate_angles_list
from astrotoolz.core.enums import CoordinateSystem
from astrotoolz.core.events.aspects.aspect import Aspect
from astrotoolz.core.events.aspects.aspect_factory import find_exact_aspects
from astrotoolz.core.events.astro_event import (
    AstroEvent,
    ExtremeEvent,
    PositionalEvent,
    TropicalProgression,
)
from astrotoolz.core.events.positional.positional_event_factory import (
    create_positional_events,
)
from astrotoolz.core.factories import (
    MappedPositionsFactory,
    PositionsFactory,
)
from astrotoolz.core.objects.points import SUN, get_default_angle_targets
from astrotoolz.core.positions.position_factory_config import PositionsFactoryConfig
from astrotoolz.core.zodiac.positions.mapped_geo_position import (
    MappedGeoPosition as MappedGeoPosition,
)
from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition as mp
from astrotoolz.tools.timeline.timeline import Timeline
from astrotoolz.tools.timeline.timeline_config import (
    AspectsConfig,
    TimelineConfig,
)
from astrotoolz.util.console_logger import ConsoleLogger

_logger = ConsoleLogger("TimelineFactory")


def create_timelines(
    configs: List[TimelineConfig],
    aggregate: bool = True,
) -> List[Timeline]:
    timelines = [create_timeline(config) for config in configs]

    if aggregate:
        return [_aggregate_timelines(timelines)]
    else:
        return timelines


def create_timeline(
    config: TimelineConfig,
) -> Timeline:
    mps = _generate_mapped_positions(
        config, config.positions_factory, config.mapped_positions_factory
    )

    events = []

    positional_event_types = [
        e
        for e in config.events
        if issubclass(e, PositionalEvent) or e is TropicalProgression
    ]

    if positional_event_types:
        events += _generate_positional_events(config, mps, positional_event_types)

    extreme_event_types = [e for e in config.events if e == ExtremeEvent]

    if extreme_event_types:
        events += _generate_extreme_events(
            config,
            mps,
            extreme_event_types,
        )

    aspects = []

    if config.aspects:
        for aspc in config.aspects:
            angles = _generate_angles(config, aspc, mps)
            aspects += _generate_aspects(aspc, angles, config.coordinate_system)

    _logger.debug(f"Identified {len(aspects)} aspects")
    return Timeline(events + aspects)


def _generate_mapped_positions(
    tl_config: TimelineConfig,
    p_factory: PositionsFactory,
    mp_factory: MappedPositionsFactory,
) -> Dict[str, List[mp]]:
    mps = {}
    for point in tl_config.points:
        _logger.info(f"Generating {tl_config.coordinate_system} positions for {point}")
        factory_config = PositionsFactoryConfig(
            tl_config.coordinate_system,
            point,
            tl_config.start_date,
            tl_config.end_date,
            tl_config.interval_minutes,
            tl_config.node_calc,
        )
        bps = p_factory(factory_config)
        mp_list = mp_factory(bps)
        mps[point] = mp_list

    return mps


def _generate_positional_events(
    tl_config: TimelineConfig,
    mps: Dict[str, List[mp]],
    event_types: List[type],
) -> List[Type[AstroEvent]]:
    events = []
    for p, mp_list in mps.items():
        _logger.info(
            f"Generating {tl_config.coordinate_system} positional events for {p}"
        )
        events += create_positional_events(mp_list, event_types)
    return events


def _generate_extreme_events(
    tl_config: TimelineConfig,
    mps: Dict[str, List[mp]],
    event_types: List[type],
) -> List[AstroEvent]:
    events = []
    for p, mp_list in mps.items():
        _logger.info(f"Generating {tl_config.coordinate_system} extreme events for {p}")
        events += _generate_extreme_events(mp_list, event_types)
    return events


def _aggregate_timelines(timelines: List[Timeline]) -> Timeline:
    _logger.info("Aggregating timelines...")
    events = []
    for timeline in timelines:
        events += timeline.events
    return Timeline(events)


def _generate_angles(
    tl_config: TimelineConfig,
    asp_config: AspectsConfig,
    mps: List[mp],
) -> List[Angle]:
    _logger.info("Generating angles")
    targets = _get_angle_targets(tl_config, asp_config)
    return generate_angles_list(
        mps,
        targets,
        tl_config.position_factory,
        tl_config.mapped_position_factory,
        tl_config.node_calc,
    )


def _get_angle_targets(
    tl_config: TimelineConfig,
    asp_config: AspectsConfig,
) -> Dict[str, List[str]]:
    ret = {}

    for p in tl_config.points:
        if not asp_config.targets:
            targets = get_default_angle_targets(p, tl_config.coordinate_system)
            if (
                SUN not in tl_config.points
                and tl_config.coordinate_system == CoordinateSystem.GEO
            ):
                targets.append(SUN)
            ret[p] = targets
        else:
            ret[p] = asp_config.targets
        _logger.debug(f"Identified angle targets for {p}: {ret[p]}")

    return ret


def _generate_aspects(
    asp_config: AspectsConfig, angles: List[Angle], coord_system: CoordinateSystem
) -> List[Aspect]:
    _logger.info("Calculating aspects...")
    asp_values = []
    if not asp_config.family:
        asp_values.append(asp_config.angle)
    else:
        asp_values = _generate_asp_family(asp_config.angle)
    return find_exact_aspects(angles, asp_config.orb, asp_values, coord_system)


def _generate_asp_family(root: float) -> List[float]:
    return [multiple for multiple in range(0, 361, root)]
