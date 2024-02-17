from dataclasses import dataclass
from typing import Dict, List

from events.aspects.aspect import Aspect
from events.aspects.aspect_finder import AspectFinder
from events.aspects.orb_map import OrbMap

from astrotoolz.core.angles.angle import Angle


@dataclass
class TransitTable:
    angles: Dict[str, List[Angle]]
    aspects: Dict[str, List[Aspect]]

    def __init__(self, angles: List[Angle]):
        self.angles = angles

        orb_map = OrbMap()
        asp_finder = AspectFinder(orb_map)
        self.aspects = asp_finder.find_aspects(self.angles)
