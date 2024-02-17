from dataclasses import dataclass
from typing import Dict

from astrotoolz.core.enums import AspectType
from astrotoolz.core.objects.points import ALL_POINTS, ANGULARS, LUMINARIES


@dataclass
class OrbMap:
    orbs: Dict[str, Dict[AspectType, int]]  # {point_name to {AspectType, orb}}

    @classmethod
    def _get_default_orbs(cls) -> Dict[str, Dict[AspectType, int]]:
        orb_map = {}
        for planet in ALL_POINTS + ANGULARS:
            asp_types_orbs = {}
            asp_types_orbs[AspectType.CONJUNCTION] = 10 if planet in LUMINARIES else 8
            asp_types_orbs[AspectType.SEXTILE] = 6 if planet in LUMINARIES else 4
            asp_types_orbs[AspectType.SQUARE] = 10 if planet in LUMINARIES else 8
            asp_types_orbs[AspectType.TRINE] = 10 if planet in LUMINARIES else 8
            asp_types_orbs[AspectType.OPPOSITION] = 10 if planet in LUMINARIES else 8
            asp_types_orbs[AspectType.QUINTILE] = 8 if planet in LUMINARIES else 6
            asp_types_orbs[AspectType.INCONJUNCT] = 5 if planet in LUMINARIES else 3
            orb_map[planet] = asp_types_orbs
        return orb_map

    @classmethod
    def _generate_orbs(cls, orb: float) -> Dict[str, Dict[AspectType, int]]:
        orb_map = {}
        for planet in ALL_POINTS + ANGULARS:
            asp_types_orbs = {}
            for asp_type in AspectType:
                asp_types_orbs[asp_type] = orb
            orb_map[planet] = asp_types_orbs
        return orb_map

    @classmethod
    def default(cls):
        return cls(cls._get_default_orbs())

    @classmethod
    def from_float(cls, orb: float):
        return cls(cls._generate_orbs(orb))

    def get_aspects_orbs(self, planet: str) -> Dict[AspectType, int]:
        return self.orbs.get(planet)
