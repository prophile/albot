from sr.robot import StationCode, Claimant
from albot.view import STATION_CODE_LOCATIONS, Location
from albot.navmesh import get_zone, is_direct_routable, get_next_hop, ZONE_CENTRES
from typing import Mapping, Sequence, Optional, Set

import math
import random


PREDECESSORS: Mapping[Claimant, Mapping[StationCode, Optional[Sequence[StationCode]]]] = {
    Claimant.ZONE_0: {
        StationCode.TH: [StationCode.PN],
        StationCode.PN: None,
        StationCode.BG: None,
        StationCode.OX: None,
        StationCode.EY: [StationCode.PN, StationCode.VB],
        StationCode.VB: [StationCode.OX, StationCode.BG],
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


def effective_distance(from_location: Location, to_location: Location, dropped: bool) -> float:
    from_zone = get_zone(from_location)
    next_hop, is_direct = get_next_hop(from_zone, to_location, dropped)
    if is_direct:
        return math.hypot(to_location.x - from_location.x, to_location.y - from_location.y)
    intermediate = ZONE_CENTRES[next_hop]
    intermediate_distance = math.hypot(intermediate.x - from_location.x, intermediate.y - from_location.y)
    return intermediate_distance + effective_distance(intermediate, to_location, dropped)


HIGH_VALUE_TARGETS = [
    StationCode.HA,
    StationCode.YT,
    StationCode.FL,
    StationCode.VB,
    StationCode.SZ,
    StationCode.PN,
]


def choose_next_target(
    zone: int,
    captured: Set[StationCode],
    disregard: Set[StationCode],
    from_location: Location,
    dropped: bool,
    pseudo_distances: Mapping[StationCode, float],
) -> StationCode:
    candidates = set()
    for station in StationCode:
        if station in captured:
            continue
        if station in disregard:
            continue
        if is_capturable(zone, station, captured):
            candidates.add(station)
    if len(candidates) == 1:
        return next(iter(candidates))
    if len(candidates) == 0:
        return random.choice(list(StationCode))
    return min(
        candidates,
        key=lambda x: (
            effective_distance(from_location, STATION_CODE_LOCATIONS[x], dropped) * (0.5 if x in HIGH_VALUE_TARGETS else 1) +
            pseudo_distances[x]
        ),
    )
