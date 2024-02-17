from dataclasses import dataclass
import datetime
from enum import Enum
from typing import List


class DasaLevel(Enum):
    MahaDasa = (1,)
    Bhukti = (2,)
    Pratyantar = (3,)
    Sookshma = (4,)
    Prana = 5


@dataclass
class Dasa:
    def __init__(
        self,
        level: DasaLevel,
        planet: str,
        start_date: datetime,
        end_date: datetime,
        sub_dasas: List["Dasa"] = None,
    ):
        self.level = level
        self.planet = planet
        self.start_date = start_date
        self.end_date = end_date
        self.sub_dasas = sub_dasas if sub_dasas is not None else []

    def __repr__(self):
        return f"{self.planet}, start: {self.start_date.strftime('%b %d, %Y')}, end: {self.end_date.strftime('%b %d, %Y')}"

    def count_sub_periods(self):
        count = len(self.sub_dasas)  # count this dasa
        for sub_dasa in self.sub_dasas:
            count += sub_dasa.count_sub_periods()  # recursively count sub-dasas
        return count
