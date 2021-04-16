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
    StationCode.BE: Location(x=0, y=-1.25),
    StationCode.BG: Location(x=-3.90, y=0),
    StationCode.BN: Location(x=6.4, y=-2.8),
    StationCode.EY: Location(x=-1.95, y=1.15),
    StationCode.FL: Location(x=0, y=2.6),
    StationCode.HA: Location(x=0, y=-0.4),
    StationCode.HV: Location(x=3.9, y=0),
    StationCode.OX: Location(x=-6.4, y=-2.80),
    StationCode.PL: Location(x=0, y=-2.6),
    StationCode.PN: Location(x=-4, y=2.00),
    StationCode.PO: Location(x=1.95, y=1.25),
    StationCode.SF: Location(x=6.25, y=3),
    StationCode.SW: Location(x=2.95, y=-2.55),
    StationCode.SZ: Location(x=1.75, y=-0.55),
    StationCode.TH: Location(x=-6.25, y=3),
    StationCode.TS: Location(x=-2.95, y=-2.55),
    StationCode.VB: Location(x=-2.15, y=-0.55),
    StationCode.YL: Location(x=4, y=2),
    StationCode.YT: Location(x=0, y=1.85),
}


@dataclasses.dataclass(frozen=True)
class View:
    heading: float
    targets: Sequence[Target]
    location: Optional[Location]
    proximity: bool
    left_distance: float
    right_distance: float
    dropped: bool


def get_world_view(R: Robot) -> View:
    heading = R.compass.get_heading()
    targets = R.radio.sweep()
    location = mlat(heading, targets)
    left_distance = R.ruggeduinos[0].analogue_read(0)
    right_distance = R.ruggeduinos[0].analogue_read(1)
    proximity = (
        left_distance < 0.05 or  # Front left ultrasound
        right_distance < 0.05 or  # Front right ultrasound
        R.ruggeduinos[0].digital_read(2)  # Front bump switch
    )
    return View(heading=heading, targets=list(targets), location=location, proximity=proximity, left_distance=left_distance, right_distance=right_distance, dropped=R.time() > 60.0)


def get_station_location(station_code: StationCode) -> Location:
    return STATION_CODE_LOCATIONS[station_code]


def single_target_position(heading: float, target: Target) -> Location:
    absolute_bearing = heading + target.bearing
    #print(f"Absolute bearing to {target.target_info.station_code} is {math.degrees(absolute_bearing):.0f}°, distance is {1.0 / target.signal_strength:.2f}m")
    distance = 1.0 / target.signal_strength
    station_location = get_station_location(target.target_info.station_code)
    return Location(
        x=station_location.x - distance * math.sin(absolute_bearing),
        y=station_location.y - distance * math.cos(absolute_bearing),
    )


def mlat(heading: float, targets: Sequence[Target]) -> Optional[Location]:
    if not targets:
        return None

    locations = [single_target_position(heading, target) for target in targets]

    loc = Location(
        x=statistics.mean(location.x for location in locations),
        y=statistics.mean(location.y for location in locations),
    )
    target_names = ", ".join(str(x.target_info.station_code) for x in targets)
    if len(locations) > 1:
        stderr = math.sqrt(
            statistics.variance(location.x for location in locations) +
            statistics.variance(location.y for location in locations)
        )
        #print(f"VOR/DME from {target_names}: {loc} (stderr is {stderr:.3f}m)")
    else:
        pass
        #print(f"VOR/DME from {target_names}: {loc} (no integrity)")

    return loc
