from dataclasses import dataclass

from astrotoolz.core.units.dms import DMS


@dataclass
class Degree:
    dms: DMS
    decimal: float
    _precision = 4  # TODO make this configurable

    @classmethod
    def from_decimal(cls, dec: float):
        if not isinstance(dec, (int, float)):
            raise TypeError("Invalid argument type")
        dms = cls._convert_from_decimal_to_zodiacal(dec)
        return cls(dms, dec)

    @classmethod
    def from_dms(cls, degrees: int, minutes: int, seconds: int):
        if degrees > 360 or minutes > 60 or seconds > 60:
            raise ValueError(f"Invalid degree values: {degrees}, {minutes}, {seconds}")
        dms = DMS(degrees, minutes, seconds)
        dec = cls._convert_from_zodiacal_to_decimal(dms)
        return cls(dms, dec)

    @staticmethod
    def _convert_from_zodiacal_to_decimal(zodiacal):
        sec = 0 if zodiacal.seconds == 0 else 60 / zodiacal.seconds
        min = zodiacal.minutes if sec == 0 else zodiacal.minutes + 1 / sec
        degree = zodiacal.degrees if min == 0 else zodiacal.degrees + 1 / (60 / min)
        return degree

    @staticmethod
    def _convert_from_decimal_to_zodiacal(dec):
        decimal_part = dec - int(dec)

        minute = decimal_part * 60
        minute_decimal_part = minute - int(minute)

        second = minute_decimal_part * 60

        return DMS(int(dec), int(minute), int(second))

    def round_to_nearest_whole(self):
        def add_one(u):
            return u + 1 if u % 10 == 9 else u

        def sixty_to_zero(u):
            return 0 if u == 60 else u

        sec = add_one(self.dms.seconds)
        min = self.dms.minutes + 1 if sec == 60 else self.dms.minutes
        deg = self.dms.degrees + 1 if min == 60 else self.dms.degrees

        return Degree(deg, sixty_to_zero(min), sixty_to_zero(sec))

    def __str__(self):
        return f"{self.decimal:.3f}° [{self.dms}]"

    def str_decimal(self):
        return f"{self.decimal:.3f}°"

    def __lt__(self, other):
        if not isinstance(other, Degree):
            return NotImplemented
        return self.decimal < other.decimal

    def __gt__(self, other):
        if not isinstance(other, Degree):
            return NotImplemented
        return self.decimal > other.decimal

    def __eq__(self, other: "Degree"):
        if not isinstance(other, Degree):
            return NotImplemented

        diff = round(self.decimal - other.decimal, self._precision)

        return diff == 0

    def __ne__(self, other: "Degree", decimals: int = 4):
        return not self.__eq__(other, decimals)
