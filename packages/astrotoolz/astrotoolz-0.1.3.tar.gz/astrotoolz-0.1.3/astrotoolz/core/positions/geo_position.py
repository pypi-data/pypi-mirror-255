from dataclasses import dataclass
from datetime import datetime as dt

from astrotoolz.core.positions.base_position import BasePosition
from astrotoolz.core.units.degree import Degree


@dataclass
class GeoPosition(BasePosition):
    ra: Degree
    dec: Degree

    def __repr__(self):
        return (
            f"Point: {self.point}\n"
            f"Datetime: {self.dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Longitude: {self.lon}\n"
            f"Latitude: {self.lat}\n"
            f"Right Ascension: {self.ra}\n"
            f"Declination: {self.dec}\n"
            f"Speed: {self.speed}"
        )
