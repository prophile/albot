import math

from sr.robot import Robot

from albot.state import State
from albot.view import View, single_target_position
from albot.navmesh import get_zone
from albot.nerf import NERF_MODE

import collections
import dataclasses


def update_state_from_view(robot: Robot, state: State, view: View) -> None:
    # Update captured
    new_captured = set(state.captured)
    for target in view.targets:
        if target.target_info.owned_by == state.zone:
            new_captured.add(target.target_info.station_code)
        else:
            if not NERF_MODE:
                # In nerf mode we pretend we're unaware of zones taken away from us
                new_captured.discard(target.target_info.station_code)
    state.captured = new_captured

    # Zone updating
    zone_list = list(state.zone_history)
    zone_list.append(get_zone(state.kalman.location))

    if len(zone_list) > 4:
        zone_list = zone_list[-4:]
    state.zone_history = zone_list

    zones = collections.Counter(zone_list)
    zones.update([zone_list[-1]])

    (element, num_instances), = zones.most_common(1)
    if num_instances > 1:
        state.current_zone = element
    else:
        state.current_zone = None

    time = robot.time()
    state.kalman.tick(
        dt=time - state.kalman_time,
        left_power=robot.motors[0].m0.power,
        right_power=robot.motors[0].m1.power,
    )
    state.kalman.update_heading(view.compass)
    for target in view.targets:
        state.kalman.update_location(
            location=single_target_position(state.kalman.heading, target),
            stdev=0.08,
        )
    state.kalman_time = time

    print(f"Position is {state.kalman.location.x:.3f}, {state.kalman.location.y:.3f} ±{state.kalman.location_error:.3f}m")
    print(f"Heading is {math.degrees(state.kalman.heading):.0f}° ±{math.degrees(state.kalman.heading_error):.0f}°")
