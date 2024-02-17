from dataclasses import dataclass
from datetime import datetime

from astrotoolz.core.enums import CoordinateSystem, NodeCalc


@dataclass
class PositionFactoryConfig:
    coordinate_system: CoordinateSystem
    point: str
    dt: datetime
    node_calc: NodeCalc = None


@dataclass
class PositionsFactoryConfig:
    coordinate_system: CoordinateSystem
    point: str
    start: datetime
    end: datetime
    interval_minutes: int
    node_calc: NodeCalc
