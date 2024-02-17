from itertools import groupby
from typing import Dict, List

from events.aspects.aspect import Aspect
from events.aspects.orb_map import OrbMap

from astrotoolz.core.angles.angle import Angle
from astrotoolz.core.enums import AspectType, CoordinateSystem


class AspectFinder:
    ASPECTS = {
        AspectType.CONJUNCTION: (0,),
        AspectType.SEXTILE: (60, 300),
        AspectType.QUINTILE: (72, 144, 216, 288),
        AspectType.SQUARE: (90, 270),
        AspectType.TRINE: (120, 240),
        AspectType.OPPOSITION: (180,),
        AspectType.INCONJUNCT: (150,),
    }

    def __init__(self, orb_map: OrbMap, aspects_include: List[AspectType]):
        self.orb_map = orb_map
        self.aspects_include = aspects_include

    def find_aspects_list(
        self, angles: List[Angle], coord_system: CoordinateSystem
    ) -> List[Aspect]:
        aspects = []

        for angle in angles:
            for asp_type in self.aspects_include:
                orbs = self.orb_map.get_aspects_orbs(angle.source.point)
                orb = orbs[asp_type]
                negative = angle.abs_diff - orb
                positive = angle.abs_diff + orb

                asp_values = self.ASPECTS[asp_type]

                for asp_value in asp_values:
                    if asp_value >= negative and asp_value <= positive:
                        asp = Aspect(
                            angle.source.dt, angle, asp_type, asp_value, coord_system
                        )
                        aspects.append(asp)
        return aspects

    def find_exact_aspects(self, angles: List[Angle]) -> List[Aspect]:
        # sort by dt to ensure that the min function will return the correct element (the first aspect when the diff is smallest)
        aspects = sorted(
            self.find_aspects_list(angles), key=lambda aspect: aspect.angle.dt
        )

        groups = groupby(
            aspects, key=lambda asp: f"{asp.asp_type.name} vs {asp.angle.target.point}"
        )

        aspects = []

        for key, group in groups:
            min_diff_asp = min(
                group, key=lambda asp: abs(asp.angle.abs_diff - asp.target_diff)
            )

            aspects.append(min_diff_asp)

        return aspects

    def find_aspects(
        self, angles: Dict[str, List[Angle]], coord_system: CoordinateSystem
    ) -> Dict[str, List[Aspect]]:
        aspects = {}

        for point, angle_list in angles.items():
            aspects[point] = self.find_aspects_list(angle_list, coord_system)
        return aspects
