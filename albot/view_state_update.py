from sr.robot import Robot

from albot.state import State
from albot.view import View, single_target_position
from albot.navmesh import get_zone

import collections
import dataclasses


def update_state_from_view(robot: Robot, state: State, view: View) -> State:
    # Update captured
    new_captured = set(state.captured)
    for target in view.targets:
        if target.target_info.owned_by == state.zone:
            new_captured.add(target.target_info.station_code)
        else:
            new_captured.discard(target.target_info.station_code)
    state = dataclasses.replace(state, captured=frozenset(new_captured))

    state = dataclasses.replace(state, initial_phase=False)

    # Zone updating
    zone_list = list(state.zone_history)
    zone_list.append(get_zone(state.kalman.location))

    if len(zone_list) > 4:
        zone_list = zone_list[-4:]
    state = dataclasses.replace(state, zone_history=zone_list)

    zones = collections.Counter(zone_list)
    zones.update([zone_list[-1]])

    (element, num_instances), = zones.most_common(1)
    if num_instances > 1:
        state = dataclasses.replace(state, current_zone=element)
    else:
        state = dataclasses.replace(state, current_zone=None)

    time = robot.time()
    state.kalman.tick(
        dt=time - state.kalman_time,
        left_power=robot.motors[0].m0.power,
        right_power=robot.motors[0].m1.power,
    )
    state.kalman.update_heading(view.compass)
    for target in view.targets:
        state.kalman.update_location(
            location=single_target_position(view.heading, target),
            stdev=0.08,
        )
    state = dataclasses.replace(state, kalman_time=time)

    print(f"Position is {state.kalman.location.x:.3f}, {state.kalman.location.y:.3f} ±{state.kalman.location_error:.3f}m")

    return state
