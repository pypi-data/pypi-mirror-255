from typing import List

from astrotoolz.tools.dasa.dasa import Dasa


def print_dasas(dasas: List[Dasa], level: int = 0) -> str:
    dasa_str = ""
    for dasa in dasas:
        dasa_str += (
            "  " * level
            + f"{dasa.level.name}: {dasa.planet}, start: {dasa.start_date.strftime('%b %d, %Y')}, end: {dasa.end_date.strftime('%b %d, %Y')}\n"
        )
        dasa_str += print_dasas(dasa.sub_dasas, level + 1)
    return dasa_str
