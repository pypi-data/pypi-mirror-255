from dataclasses import dataclass

@dataclass
class DMS:
    degrees: int
    minutes: int
    seconds: int

    def __str__(self):
        return f"{self.degrees}°{self.minutes}'{self.seconds}''"
