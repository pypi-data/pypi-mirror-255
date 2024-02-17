from core.angles.angle import Angle
from core.enums import CoordinateSystem, NodeCalc
from core.factories import MappedPositionFactory, PositionFactory
from typing import Callable, Dict, List
from core.positions.position_factory_config import PositionFactoryConfig

from core.zodiac.positions.mapped_position import MappedPosition
from util.console_logger import ConsoleLogger


_logger = ConsoleLogger("AngleFactory")


def generate_angles_dict(
    mps: List[MappedPosition], target_selector: Callable[[str], List[str]]
) -> Dict[str, List[Angle]]:
    angles = {}
    for mp in mps:
        targets = target_selector(mp.point)

        angles[mp.point] = []

        for t in targets:
            target_mp = next((p for p in mps if p.point == t), None)
            if target_mp is not None:
                angle = Angle(mp, target_mp)
                angles[mp.point].append(angle)

    return angles


def generate_angles_list(
    mps: Dict[str, List[MappedPosition]],
    targets: Dict[str, List[str]],
    p_factory: PositionFactory,
    mp_factory: MappedPositionFactory,
    node_calc: NodeCalc,
) -> List[Angle]:
    angles = []
    for p, mp_list in mps.items():
        current_targets = targets[p]

        _logger.info(f"Generating angles for {p}")

        for source_mp in mp_list:
            for t in current_targets:
                if t == source_mp.point:
                    continue

                cfg = PositionFactoryConfig(
                    CoordinateSystem.GEO, t, source_mp.dt, node_calc
                )

                target_bp = p_factory(cfg)
                target_mp = mp_factory(target_bp)
                angle = Angle(source_mp, target_mp)
                angles.append(angle)

    return angles
