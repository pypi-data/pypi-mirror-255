from dataclasses import dataclass
from typing import List

import astrotoolz.core.ephemeris.swisseph_api as swe_api
import astrotoolz.core.zodiac.division as zd
from astrotoolz.core.positions.base_position import BasePosition
from astrotoolz.core.positions.geo_position import GeoPosition
from astrotoolz.core.units.degree import Degree


@dataclass
class VedicAttributes:
    _root_position: BasePosition
    lon: Degree
    position: str
    sign: zd.Sign
    sign_ruler: str
    nakshatra: zd.Nakshatra
    nakshatra_ruler: str

    def __init__(self, root_position: BasePosition):
        self._root_position = root_position
        self.lon = self._calculate_sidereal_lon()
        self.position = zd.degree_to_zodiacal(self.lon)
        self.sign = zd.map_sign(self.lon.decimal)
        self.sign_ruler = self.sign.vedic_ruler
        self.nakshatra = zd.map_nakshatra(self.lon.decimal)
        self.nakshatra_ruler = self.nakshatra.ruler

    def house(self, cusps: List[float] = None) -> int:
        if cusps is None:
            return self.sign.id

        return zd.calculate_house(self.lon.decimal, cusps)

    # TODO Lahiri hardcoded
    def _calculate_sidereal_lon(self) -> Degree:
        ayanamsa = swe_api.get_ayanamsha(
            self._root_position.dt.year, self._root_position.dt.month, "LAHIRI"
        )
        subtracted = self._root_position.lon.decimal - ayanamsa
        if subtracted < 0:
            subtracted = 360 + subtracted
        return Degree.from_decimal(subtracted)

    def __repr__(self):
        return (
            f"Longitude: {self.lon}, "
            f"Position: {self.position}, "
            f"Sign: {self.sign}, "
            f"Sign Ruler: {self.sign_ruler}, "
            f"Nakshatra: {self.nakshatra}, "
            f"Nakshatra Ruler: {self.nakshatra_ruler}"
        )
