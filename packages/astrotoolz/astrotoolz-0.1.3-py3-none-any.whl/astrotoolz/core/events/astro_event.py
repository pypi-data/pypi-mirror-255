from dataclasses import dataclass
from datetime import datetime

from astrotoolz.core.zodiac.positions.mapped_geo_position import MappedGeoPosition as mp


@dataclass
class AstroEvent:
    dt: datetime  # UTC

    def tv_timestamp(self) -> str:
        """eg. timestamp("2023-02-27 11:05 UTC")"""
        return f'timestamp("{self.dt.strftime("%Y-%m-%d %H:%M UTC")}")'


@dataclass
class PositionalEvent(AstroEvent):
    previous: mp
    current: mp


@dataclass
class TropicalSignChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tTropical\tSign change\t{self.previous.tropical.sign.name} -> {self.current.tropical.sign.name}"

    def label(self) -> str:
        return f"{self.current.point} TropicalSignChange {self.previous.tropical.sign.name} -> {self.current.tropical.sign.name}"


@dataclass
class SiderealSignChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tSidereal\tSign change\t{self.previous.vedic.sign.name} -> {self.current.vedic.sign.name}"

    def label(self) -> str:
        return f"{self.current.point} SiderealSignChange {self.previous.vedic.sign.name} -> {self.current.vedic.sign.name}"


@dataclass
class DecanChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tTropical\tDecan change\t{self.previous.tropical.decan.name} -> {self.current.tropical.decan.name}"

    def label(self) -> str:
        return f"{self.current.point} DecanChange {self.previous.tropical.decan.name} -> {self.current.tropical.decan.name}"


@dataclass
class TermChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tTropical\tTerm change\t{self.previous.tropical.term.name} -> {self.current.tropical.term.name}"

    def label(self) -> str:
        return f"{self.current.point} TermChange {self.previous.tropical.term.name} -> {self.current.tropical.term.name}"


@dataclass
class NakshatraChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tSidereal\tNakshatra change\t{self.previous.vedic.nakshatra.name} -> {self.current.vedic.nakshatra.name}"

    def label(self) -> str:
        return f"{self.current.point} NakshatraChange {self.previous.vedic.nakshatra.name}[{self.previous.vedic.nakshatra.ruler}] -> {self.current.vedic.nakshatra.name}[{self.current.vedic.nakshatra.ruler}]"


@dataclass
class DirectionChange(PositionalEvent):
    def __repr__(self) -> str:
        return f"{self.current.dt}\t{self.current.point}\t{self.current.cs}\tDirection change\t{self.previous.direction} -> {self.current.direction}"

    def label(self) -> str:
        return f"{self.current.point} DirectionChange {self.previous.direction} -> {self.current.direction}"


@dataclass
class ExtremeEvent(AstroEvent):
    mp: mp
    type: str  # min, max


@dataclass
class DeclinationExtreme(ExtremeEvent):
    def __repr__(self) -> str:
        return f"{self.dt}\t{self.mp.point}\t Declination {self.type} of {self.mp.base_position.dec.str_decimal()} at \t{self.mp.tropical.position}"


@dataclass
class LatitudeExtreme(ExtremeEvent):
    def __repr__(self) -> str:
        return f"{self.dt}\t{self.mp.point}\t Latitude {self.type} of {self.mp.base_position.lat.str_decimal()} at\t{self.mp.tropical.position}"


@dataclass
class SpeedExtreme(ExtremeEvent):
    def __repr__(self) -> str:
        return f"{self.dt}\t{self.mp.point}\t Speed {self.type} of {self.mp.base_position.speed.str_decimal()} at\t{self.mp.tropical.position}"


@dataclass
class PhaseExtreme(ExtremeEvent):
    def __repr__(self) -> str:
        return f"{self.dt}\t{self.mp.point}\t Phase {self.type} of {self.mp.phase.str_decimal()} at\t{self.mp.tropical.position}"


@dataclass
class TropicalProgression(AstroEvent):
    name: str

    def __repr__(self) -> str:
        return f"{self.dt}\t{self.current.point}\t{self.name} progression at\t{self.current.tropical.position}"

    def label(self) -> str:
        return f"{self.current.point} {self.name} progression at {self.current.tropical.position}"
