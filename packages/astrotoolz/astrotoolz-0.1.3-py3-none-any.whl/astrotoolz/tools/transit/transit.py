from dataclasses import dataclass
from typing import List

from astrotoolz.core.angles.angle import Angle
from astrotoolz.tools.horoscope.horoscope import Horoscope
from astrotoolz.tools.transit.transit_table import TransitTable


@dataclass
class Transit:
    natal_horoscope: Horoscope
    transit_horoscope: Horoscope

    def __init__(self, natal_horoscope: Horoscope, transit_horoscope: Horoscope):
        self.natal_horoscope = natal_horoscope
        self.transit_horoscope = transit_horoscope

        if (
            self.natal_horoscope.coord_system != self.transit_horoscope.coord_system
            or self.natal_horoscope.house_system != self.transit_horoscope.house_system
            or self.natal_horoscope.zodiac_system
            != self.transit_horoscope.zodiac_system
        ):
            raise Exception("Incompatible horoscopes")

    def generate_transit_table(self, points_filter: List[str] = []) -> TransitTable:
        angles = {}
        for point in [
            p
            for p in self.natal_horoscope.mgps
            if p.base_position.point not in points_filter
        ]:
            point_angles = []
            for transit_point in [
                tp
                for tp in self.transit_horoscope.mgps
                if tp.base_position.point not in points_filter
            ]:
                angle = Angle(
                    transit_point.base_position.dt,
                    point.base_position,
                    transit_point.base_position,
                )
                point_angles.append(angle)
            angles[point.base_position.point] = point_angles
        return TransitTable(angles)
