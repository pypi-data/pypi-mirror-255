from dataclasses import dataclass
from datetime import datetime

from astrotoolz.core.zodiac.positions.mapped_position import MappedPosition


@dataclass
class Angle:
    dt: datetime
    source: MappedPosition
    target: MappedPosition

    def __init__(self, source: MappedPosition, target: MappedPosition):
        self.source = source
        self.target = target
        self.dt = source.dt

    @property
    def abs_diff(self):
        return abs(
            self.source.base_position.lon.decimal
            - self.target.base_position.lon.decimal
        )

    @property
    def real_diff(self):
        return (
            self.source.base_position.lon.decimal
            - self.target.base_position.lon.decimal
        )

    @property
    def circular_diff(self):
        diff = (
            self.source.base_position.lon.decimal
            - self.target.base_position.lon.decimal
        )
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        return diff
