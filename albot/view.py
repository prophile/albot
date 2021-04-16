from typing import Sequence, Optional, Tuple

import math
import statistics
import dataclasses

from sr.robot import Robot
from sr.robot.radio import Target, StationCode


@dataclasses.dataclass(frozen=True)
class Location:
    x: float
    y: float


STATION_CODE_LOCATIONS = {
    StationCode.BE: Location(x=0, y=-1.5),
    StationCode.BG: Location(x=-4.2, y=0),
    StationCode.BN: Location(x=6.6, y=-3),
    StationCode.EY: Location(x=-1.95, y=0.75),
    StationCode.FL: Location(x=0, y=3),
    StationCode.HA: Location(x=0, y=0),
    StationCode.HV: Location(x=4.2, y=0),
    StationCode.OX: Location(x=-6.6, y=-3),
    StationCode.PL: Location(x=0, y=-3),
    StationCode.PN: Location(x=-4.2, y=1.8),
    StationCode.PO: Location(x=1.95, y=0.75),
    StationCode.SF: Location(x=6.6, y=3),
    StationCode.SW: Location(x=2.75, y=-2.75),
    StationCode.SZ: Location(x=1.95, y=-0.75),
    StationCode.TH: Location(x=-6.6, y=3),
    StationCode.TS: Location(x=-2.75, y=-2.75),
    StationCode.VB: Location(x=-1.95, y=-0.75),
    StationCode.YL: Location(x=4.2, y=1.8),
    StationCode.YT: Location(x=0, y=1.5),
}


@dataclasses.dataclass(frozen=True)
class View:
    heading: float
    targets: Sequence[Target]
    proximity: bool
    left_distance: float
    right_distance: float
    dropped: bool


def get_world_view(R: Robot) -> View:
    heading = R.compass.get_heading()
    targets = R.radio.sweep()
    left_distance = R.ruggeduinos[0].analogue_read(0)
    right_distance = R.ruggeduinos[0].analogue_read(1)
    proximity = (
        left_distance < 0.05 or  # Front left ultrasound
        right_distance < 0.05 or  # Front right ultrasound
        R.ruggeduinos[0].digital_read(2)  # Front bump switch
    )
    return View(
        heading=heading,
        targets=list(targets),
        proximity=proximity,
        left_distance=left_distance,
        right_distance=right_distance,
        dropped=R.time() > 60.0,
    )


def get_station_location(station_code: StationCode) -> Location:
    return STATION_CODE_LOCATIONS[station_code]


def single_target_position(heading: float, target: Target) -> Location:
    absolute_bearing = heading + target.bearing
    #print(f"Absolute bearing to {target.target_info.station_code} is {math.degrees(absolute_bearing):.0f}°, distance is {1.0 / target.signal_strength:.2f}m")
    distance = target.signal_strength ** -0.5
    station_location = get_station_location(target.target_info.station_code)
    return Location(
        x=station_location.x - distance * math.sin(absolute_bearing),
        y=station_location.y - distance * math.cos(absolute_bearing),
    )
