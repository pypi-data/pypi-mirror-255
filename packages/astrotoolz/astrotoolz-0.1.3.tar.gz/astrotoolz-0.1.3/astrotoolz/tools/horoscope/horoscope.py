from datetime import datetime
from typing import Dict, List, Optional

from astrotoolz.core.angles.angle import Angle
from astrotoolz.core.events.aspects.aspect import Aspect
from astrotoolz.core.objects.points import SUN
from astrotoolz.core.units.degree import Degree
from astrotoolz.core.zodiac.positions.mapped_geo_position import MappedGeoPosition
from astrotoolz.tools.horoscope.horoscope_config import HoroscopeConfig


class Horoscope:
    dt: datetime
    config: HoroscopeConfig
    mgps: List[MappedGeoPosition]
    pmgps: List[MappedGeoPosition]
    angles: Dict[str, List[Angle]]
    aspects: Dict[str, List[Aspect]]
    cusps: List[float]

    def __init__(
        self,
        dt: datetime,
        config: HoroscopeConfig,
        mps: List[MappedGeoPosition],
        pmgps: List[MappedGeoPosition],
        angles: Dict[str, List[Angle]],
        aspects: Dict[str, List[Aspect]],
        cusps: List[float],
    ):
        self.dt = dt
        self.config = config
        self.mgps = mps
        self.pmgps = pmgps
        self.angles = angles
        self.aspects = aspects
        self.cusps = cusps

    @property
    def ascendant(self):
        return self.ascmc[0]

    @property
    def mc(self):
        return self.ascmc[1]

    @property
    def ic(self):
        ic = self.mc + 180
        if ic > 360:
            ic -= 360
        return ic

    @property
    def dc(self):
        dc = self.ascendant + 180
        if dc > 360:
            dc -= 360
        return dc

    def get_daily_index(self, point: str, field_name: str) -> str:
        mgp = next(mgp for mgp in self.mgps if mgp.point == point)
        pmgp = (
            next(pmgp for pmgp in self.pmgps if pmgp.point == point)
            if self.pmgps is not None
            else None
        )

        if pmgp is None:
            return ""

        if field_name == "dec":
            return self._get_index(mgp.base_position.dec, pmgp.base_position.dec)
        elif field_name == "lat":
            return self._get_index(mgp.base_position.lat, pmgp.base_position.lat)
        elif field_name == "speed":
            return self._get_index(mgp.base_position.speed, pmgp.base_position.speed)
        elif field_name == "phase":
            phase_today = self.phase(point)
            phase_yesterday = self._phase(point, self.pmgps)
            return self._get_index(phase_today, phase_yesterday)

    def phase(self, point: str) -> Optional[Degree]:
        return self._phase(point, self.mgps)

    def _phase(self, point: str, list: List[MappedGeoPosition]) -> Optional[Degree]:
        source = next(mgp for mgp in list if mgp.point == point)
        sun = next(mgp for mgp in list if mgp.point == SUN)

        if sun is None:
            return None
        return Degree.from_decimal(Angle(source, sun).circular_diff)

    def _get_index(self, current_degree: Degree, previous_degree: Degree) -> str:
        if current_degree == previous_degree:
            return "="
        elif current_degree > previous_degree:
            return "+"
        elif current_degree < previous_degree:
            return "-"
