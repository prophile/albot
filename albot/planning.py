from sr.robot import StationCode, Claimant
from albot.view import STATION_CODE_LOCATIONS, Location
from albot.navmesh import get_zone, is_direct_routable
from typing import Mapping, Sequence, Optional, Set

from functools import lru_cache

import math


PREDECESSORS: Mapping[Claimant, Mapping[StationCode, Optional[Sequence[StationCode]]]] = {
    Claimant.ZONE_0: {
        StationCode.TH: [StationCode.PN],
        #StationCode.PN: None,
        #StationCode.BG: None,
        StationCode.PN: [StationCode.BG],
        StationCode.BG: [StationCode.VB],
        StationCode.VB: [StationCode.OX],
        #
        StationCode.OX: None,
        StationCode.EY: [StationCode.PN, StationCode.VB],
        #StationCode.VB: [StationCode.OX, StationCode.BG],
        StationCode.PL: [StationCode.VB],
        StationCode.BE: [StationCode.VB],
        StationCode.HA: [StationCode.BE],
        StationCode.YT: [StationCode.HA],
        StationCode.FL: [StationCode.EY],
        StationCode.SZ: [StationCode.BE, StationCode.PL],
        StationCode.PO: [StationCode.FL, StationCode.SZ],
        StationCode.HV: [StationCode.SZ],
        StationCode.YL: [StationCode.PO],
        StationCode.SF: [StationCode.YL],
        StationCode.BN: [StationCode.SZ],
        StationCode.SW: [StationCode.BN],
        StationCode.TS: [StationCode.OX],
    },
    Claimant.ZONE_1: {
        StationCode.YL: None,
        StationCode.SF: [StationCode.YL],
        StationCode.HV: None,
        StationCode.BN: None,
        StationCode.SW: [StationCode.BN],
        StationCode.SZ: [StationCode.BN, StationCode.HV],
        StationCode.PO: [StationCode.HV, StationCode.YL],
        StationCode.FL: [StationCode.PO],
        StationCode.BE: [StationCode.SZ],
        StationCode.PL: [StationCode.SZ],
        StationCode.HA: [StationCode.BE],
        StationCode.YT: [StationCode.HA],
        StationCode.VB: [StationCode.PL, StationCode.BE],
        StationCode.EY: [StationCode.FL, StationCode.VB],
        StationCode.PN: [StationCode.EY],
        StationCode.TH: [StationCode.PN],
        StationCode.BG: [StationCode.VB],
        StationCode.OX: [StationCode.VB],
        StationCode.TS: [StationCode.OX],
    },
}


def is_capturable(zone: int, station: StationCode, captured: Set[StationCode]) -> bool:
    predecessors = PREDECESSORS[Claimant(zone)][station]
    if predecessors is None:
        return True
    else:
        return any(x in captured for x in predecessors)


@lru_cache(maxsize=16)
def _choose_candidate_targets(zone: int, captured: Set[StationCode], disregard: Set[StationCode]) -> Set[StationCode]:
    candidates = set()
    for station_code, predecessors in PREDECESSORS[Claimant(zone)].items():
        if station_code in disregard:
            print(f"> Disconsidered {station_code} by order")
            continue
        if station_code in captured:
            print(f"> Disconsidered {station_code} because we believe it already captured")
            continue
        if predecessors is None:
            print(f"> {station_code} requires no predecessors")
            candidates.add(station_code)
        else:
            predecessors_captured = captured & set(predecessors)
            if predecessors_captured:
                pred_list = ", ".join(str(x) for x in predecessors_captured)
                print(f"> {station_code} meets predecessors {pred_list}")
                candidates.add(station_code)
            else:
                print(f"> {station_code} requires a predecessor but none are met")
    return frozenset(candidates)


def choose_next_target(zone: int, captured: Set[StationCode], disregard: Set[StationCode], from_location: Location, dropped: bool) -> StationCode:
    candidates = _choose_candidate_targets(zone, captured, disregard)
    if not candidates:
        return StationCode.OX if zone == 0 else StationCode.BN
    from_zone = get_zone(from_location)
    def candidate_distance(x):
        location = STATION_CODE_LOCATIONS[x]
        zone_score = 2
        to_zone = get_zone(location)
        if to_zone == from_zone:
            zone_score = 0
        elif is_direct_routable(from_zone, location, dropped):
            zone_score = 1
        return (zone_score, math.hypot(location.x - from_location.x, location.y - from_location.y))
    return min(candidates, key=candidate_distance)
