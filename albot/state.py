import math
import dataclasses
from typing import Set, Optional, Sequence, Mapping

from sr.robot import Robot, StationCode
from albot.pid import PIDController
from albot.view import Location
from albot.navmesh import Zone
from albot.kalman import KalmanFilter


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
    kalman: KalmanFilter
    kalman_time: float
    num_captures: Mapping[StationCode, int]


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
        kalman=KalmanFilter(
            initial_position=(
                Location(x=-7, y=0)
                if robot.zone == 0
                else Location(x=7, y=0)
            ),
            initial_heading=(
                math.radians(90)
                if robot.zone == 0
                else math.radians(270)
            ),
        ),
        kalman_time=robot.time(),
        num_captures={
            x: 0
            for x in StationCode
        },
    )
