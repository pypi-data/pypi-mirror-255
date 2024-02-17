from datetime import datetime as dt
from datetime import timezone
from typing import List

import astrotoolz.core.ephemeris.swisseph_api as swe_api
from astrotoolz.core.enums import CoordinateSystem, NodeCalc
from astrotoolz.core.objects.points import MOON, NN, PLANETS, SN, SUN
from astrotoolz.core.positions.base_position import BasePosition
from astrotoolz.core.positions.geo_position import GeoPosition
from astrotoolz.core.positions.helio_position import HelioPosition
from astrotoolz.core.positions.position_factory_config import (
    PositionFactoryConfig,
    PositionsFactoryConfig,
)
from astrotoolz.core.units.degree import Degree
from astrotoolz.util.console_logger import ConsoleLogger
from astrotoolz.util.interval import calculate_intervals

_logger = ConsoleLogger("PositionFactory")


def create_position(point: str, dt: dt, coord_system: CoordinateSystem) -> BasePosition:
    return (
        create_geo_position(point, dt)
        if coord_system == CoordinateSystem.GEO
        else create_helio_position(point, dt)
    )


def create_positions(config: PositionsFactoryConfig) -> List[BasePosition]:
    if config.coordinate_system == CoordinateSystem.HELIO:
        return create_helio_positions(config)
    else:
        return create_geo_positions(config)


def create_helio_positions(config: PositionsFactoryConfig) -> List[HelioPosition]:
    _logger.debug(f"Generating positions for config: {config}")
    dts = calculate_intervals(config.start, config.end, config.interval_minutes)
    return [
        create_helio_position(
            PositionFactoryConfig(config.coordinate_system, config.point, dt)
        )
        for dt in dts
    ]


def create_geo_positions(config: PositionsFactoryConfig) -> List[GeoPosition]:
    _logger.debug(f"Generating positions for config: {config}")
    dts = calculate_intervals(config.start, config.end, config.interval_minutes)
    return [
        create_geo_position(
            PositionFactoryConfig(
                config.coordinate_system, config.point, dt, config.node_calc
            )
        )
        for dt in dts
    ]


def create_helio_position(config: PositionFactoryConfig) -> HelioPosition:
    config.dt = config.dt.replace(tzinfo=timezone.utc)
    if config.point in [SUN, MOON, NN, SN]:
        raise (ValueError(f"{config.point} not supported"))
    else:
        return _helio(config.point, config.dt)


def create_geo_position(config: PositionFactoryConfig) -> GeoPosition:
    config.dt = config.dt.replace(tzinfo=timezone.utc)
    if config.point in PLANETS:
        return _geo(config.point, config.dt)
    elif config.point == NN:
        return _north_node(config.dt, config.node_calc)
    elif config.point == SN:
        return _south_node(config.dt, config.node_calc)
    else:
        raise (ValueError(f"{config.point} not supported"))


def _helio(point: str, dt: dt) -> HelioPosition:
    lon, lat, speed = swe_api.get_helio_position(point, dt)
    lon, lat, speed = _to_degree(lon, lat, speed)
    return HelioPosition(dt, point, lon, lat, speed)


def _geo(planet_name: str, dt: dt) -> GeoPosition:
    lon, lat, speed = swe_api.get_ecliptic_position(planet_name, dt)
    ra, dec = swe_api.get_equatorial_position(planet_name, dt)
    lon, lat, speed, ra, dec = _to_degree(lon, lat, speed, ra, dec)
    return GeoPosition(dt, planet_name, lon, lat, speed, ra, dec)


def _north_node(dt: dt, node_calc: NodeCalc) -> GeoPosition:
    pos = _geo(node_calc.swe_flag(), dt)
    pos.point = NN
    return pos


def _south_node(dt: dt, node_calc: NodeCalc) -> GeoPosition:
    nn = _north_node(dt, node_calc.swe_flag())
    lon = (nn.lon.decimal + 180.0) % 360
    lat = 0
    speed = nn.speed.decimal
    ra = (nn.ra.decimal + 12.0) % 24.0
    dec = -nn.dec.decimal
    lon, lat, speed, ra, dec = _to_degree(lon, lat, speed)
    return GeoPosition(dt, SN, lon, lat, speed, ra, dec)


def _to_degree(*args: float) -> List[Degree]:
    return [Degree.from_decimal(arg) for arg in args]
