from albot.state import State
from albot.view import View
from albot.navmesh import get_zone

import collections
import dataclasses


def update_state_from_view(state: State, view: View) -> State:
    # Update captured
    new_captured = set(state.captured)
    for target in view.targets:
        if target.target_info.owned_by == state.zone:
            new_captured.add(target.target_info.station_code)
        else:
            new_captured.discard(target.target_info.station_code)
    state = dataclasses.replace(state, captured=frozenset(new_captured))

    if view.location is not None:
        state = dataclasses.replace(state, initial_phase=False)

        # Zone updating
        zone_list = list(state.zone_history)
        zone_list.append(get_zone(view.location))

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

    return state
