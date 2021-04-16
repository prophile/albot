import math
import dataclasses
from typing import Set, Optional, Sequence

from sr.robot import Robot, StationCode
from albot.pid import PIDController
from albot.navmesh import Zone


@dataclasses.dataclass(frozen=True)
class State:
    zone: int
    heading_pid: PIDController
    captured: Set[StationCode]
    uncapturable: Set[StationCode]
    current_target: Optional[StationCode]
    initial_phase: bool
    current_zone: Optional[Zone]
    zone_history: Sequence[Zone]


def initial_state(robot: Robot) -> State:
    return State(
        zone=robot.zone,
        heading_pid=PIDController(
            full_deflection_error=math.radians(120),
            prediction_time=0.3,
            fine_tune_time=2.0,
            time=lambda: robot.time(),
        ),
        captured=frozenset(),
        uncapturable=frozenset(),
        current_target=None,
        initial_phase=True,
        current_zone=None,
        zone_history=[],
    )
