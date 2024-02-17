from dataclasses import dataclass

from astrotoolz.core.enums import CoordinateSystem
from astrotoolz.core.positions.geo_position import GeoPosition
from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition


@dataclass
class MappedGeoPosition(MappedPosition):
    base_position: GeoPosition
    retrograde: bool
    stationary: bool
    direction: str

    def __init__(
        self,
        base_position: GeoPosition,
    ):
        self.base_position = base_position
        self.retrograde = self.base_position.speed.decimal < 0
        self.stationary = self.base_position.speed.decimal == 0
        self.direction = "R" if self.retrograde else "S" if self.stationary else "D"
        self.cs = CoordinateSystem.GEO
