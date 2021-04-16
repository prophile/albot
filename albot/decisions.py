from typing import Tuple

from sr.robot import Robot, StationCode
from albot.state import State
from albot.view import View, get_station_location
from albot.navmesh import get_next_hop, ZONE_CENTRES, get_zone
from albot.actions import Action, DoNothing, ClaimImmediate, BackOff, GotoStation, MoveRandomly, GoHeading, GotoLocation
from albot.planning import is_capturable, choose_next_target

import random
import dataclasses


BEES = []


def choose_action(robot: Robot, state: State, view: View) -> Tuple[Action, State]:
    # Consider immediate claim targets, where we're already within the territory
    for target in view.targets:
        if 1.0 / target.signal_strength > 0.22:
            continue

        if target.target_info.owned_by == robot.zone:
            #print(f"> Considered {target.target_info.station_code} but we already own it")
            continue

        if not is_capturable(state.zone, target.target_info.station_code, state.captured):
            print(f"> Considered {target.target_info.station_code} but we believe we're missing a predecessor")
            continue

        if target.target_info.station_code in state.uncapturable:
            print(f"> Considered {target.target_info.station_code} but skipping due to previous difficulties")
            continue

        return ClaimImmediate(target.target_info.station_code), state

    # Back off if we're in proximity
    if view.proximity:
        if random.random() < 0.95:
            return BackOff(), state
        else:
            return MoveRandomly(), state

    if (
        state.current_target is not None and
        state.current_target not in state.captured and
        state.current_target not in state.uncapturable and
        is_capturable(state.zone, state.current_target, state.captured)
    ):
        target = state.current_target
    else:
        target = choose_next_target(state.zone, state.captured, state.uncapturable, from_location=state.kalman.location, dropped=view.dropped)
        state = dataclasses.replace(state, current_target=target)

    next_hop, route_direct = get_next_hop(get_zone(state.kalman.location), get_station_location(target), view.dropped)
    if route_direct:
        return GotoStation(target), state
    else:
        print(f"Routing to {target} via {next_hop}")
        return GotoLocation(ZONE_CENTRES[next_hop]), state
