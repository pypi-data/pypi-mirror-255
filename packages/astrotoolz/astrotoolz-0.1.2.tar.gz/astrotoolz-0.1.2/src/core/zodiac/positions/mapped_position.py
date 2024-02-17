from dataclasses import dataclass
from datetime import datetime
from typing import List
from core.enums import CoordinateSystem
from core.positions.base_position import BasePosition
from core.units.degree import Degree
from util.cached_property import CachedProperty
from core.zodiac.attributes.tropical_attributes import TropicalAttributes
from core.zodiac.attributes.vedic_attributes import VedicAttributes


@dataclass
class MappedPosition:
    cs: CoordinateSystem

    def __init__(self, base_position: BasePosition):
        self.base_position = base_position
        self.cs = None

    @classmethod
    def from_planetary_positions(cls, planetary_positions: List[BasePosition]):
        return [cls(position) for position in planetary_positions]

    @property
    def dt(self) -> datetime:
        return self.base_position.dt

    @property
    def point(self) -> str:
        return self.base_position.point

    @CachedProperty
    def tropical(self) -> TropicalAttributes:
        return TropicalAttributes(self.base_position)

    @CachedProperty
    def vedic(self) -> VedicAttributes:
        return VedicAttributes(self.base_position)
