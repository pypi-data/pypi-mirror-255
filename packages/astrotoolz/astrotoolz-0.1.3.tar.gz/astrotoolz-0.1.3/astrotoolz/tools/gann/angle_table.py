from dataclasses import dataclass
from datetime import datetime
from typing import List

from astrotoolz.core.angles.angle_factory import generate_angles_dict
from astrotoolz.core.enums import CoordinateSystem
from astrotoolz.core.objects.points import get_default_angle_targets
from astrotoolz.core.positions.position_factory import create_position
from astrotoolz.core.zodiac.positions.mapped_geo_position import MappedGeoPosition
from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition


@dataclass
class AngleTable:
    def __init__(
        self, dt: datetime, planets: List[str], coord_system: CoordinateSystem
    ):
        bps = [create_position(p, dt, coord_system) for p in planets]
        self.mps = (
            MappedGeoPosition.from_planetary_positions(bps)
            if coord_system == CoordinateSystem.GEO
            else MappedPosition.from_planetary_positions(bps)
        )
        self.angles = generate_angles_dict(self.mps, get_default_angle_targets)
