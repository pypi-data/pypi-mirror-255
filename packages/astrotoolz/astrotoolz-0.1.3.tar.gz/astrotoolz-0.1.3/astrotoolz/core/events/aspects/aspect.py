from dataclasses import dataclass

from astrotoolz.core.angles.angle import Angle
from astrotoolz.core.enums import AspectType, CoordinateSystem
from astrotoolz.core.events.astro_event import AstroEvent

DEFAULT_ASPECTS = [
    AspectType.CONJUNCTION,
    AspectType.OPPOSITION,
    AspectType.SQUARE,
    AspectType.TRINE,
    AspectType.SEXTILE,
    AspectType.INCONJUNCT,
    AspectType.QUINTILE,
]


@dataclass
class Aspect(AstroEvent):
    angle: Angle
    asp_type: str
    target_diff: int
    coord_system: CoordinateSystem

    @property
    def asp_text(self):
        return f"{self.angle.source.point} {self.asp_type} vs {self.angle.target.point}"

    def __repr__(self):
        # return f"aspect at {self.angle}, {self.asp_str} ({self.asp_diff})\n Orb of 2 starts at: {orb_start}, ends at: {orb_end}"
        return f"{self.dt}\t{self.angle.source.point}\t{self.coord_system}\t{self.asp_type.lower()} [{self.angle.abs_diff:.3f}] vs {self.angle.target.point} at [{self.angle.source.tropical.lon.decimal:.3f}]"

    def label(self):
        return f"{self.angle.source.point} {self.asp_type.lower()} [{self.angle.abs_diff:.0f}] vs {self.angle.target.point} at [{self.angle.source.tropical.lon.decimal:.3f}]"

    def print_tropical_no_time(self):
        return f"{self.angle.source.point} [{self.angle.source.tropical.lon.decimal:.3f}], {self.angle.target.point} [{self.angle.target.tropical.lon.decimal:.3f}], {self.angle.abs_diff:.3f}"

    def print_vedic_no_time(self):
        return f"{self.source.point} [{self.source.vedic.lon.decimal:.3f}], {self.target.point} [{self.target.vedic.lon.decimal:.3f}], {self.diff:.3f}"
