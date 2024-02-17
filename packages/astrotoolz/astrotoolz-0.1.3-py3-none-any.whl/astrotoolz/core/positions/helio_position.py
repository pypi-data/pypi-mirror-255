from dataclasses import dataclass

from astrotoolz.core.positions.base_position import BasePosition


@dataclass
class HelioPosition(BasePosition):
    def __repr__(self):
        return (
            f"Point: {self.point}\n"
            f"Datetime: {self.dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Longitude: {self.lon}\n"
            f"Latitude: {self.lat}\n"
            f"Speed: {self.speed}"
        )
