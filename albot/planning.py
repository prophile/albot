from sr.robot import StationCode, Claimant
from albot.view import STATION_CODE_LOCATIONS, Location
from albot.navmesh import get_zone, is_direct_routable
from typing import Mapping, Sequence, Optional, Set

import math


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


CAPTURE_SEQUENCES: Mapping[Claimant, Sequence[StationCode]] = {
    Claimant.ZONE_0: [
        StationCode.PN,
        StationCode.EY,
        StationCode.FL,
        StationCode.PO,
        StationCode.SZ,
        StationCode.BE,
        StationCode.HA,
        StationCode.YT,
#

        StationCode.OX,
        StationCode.TS,
        StationCode.VB,
        StationCode.BE,
        StationCode.HA,
        StationCode.SZ,
        StationCode.PL,
        StationCode.HV,
        StationCode.PO,
        StationCode.YT,
        StationCode.FL,
        StationCode.EY,
        StationCode.PN,
        StationCode.BN,
        StationCode.TH,
        StationCode.SF,
        StationCode.BN,
        StationCode.SW,
    ],
    Claimant.ZONE_1: [
        StationCode.BN,
        StationCode.SW,
        StationCode.SZ,
        StationCode.BE,
        StationCode.HA,
        StationCode.VB,
        StationCode.PL,
        StationCode.OX,
        StationCode.TS,
        StationCode.BG,
        StationCode.EY,
        StationCode.YT,
        StationCode.FL,
        StationCode.PO,
        StationCode.YL,
        StationCode.HV,
        StationCode.SF,
        StationCode.TH,
        StationCode.OX,
        StationCode.TS,
    ],
}


def is_capturable(zone: int, station: StationCode, captured: Set[StationCode]) -> bool:
    predecessors = PREDECESSORS[Claimant(zone)][station]
    if predecessors is None:
        return True
    else:
        return any(x in captured for x in predecessors)


def choose_next_target(zone: int, captured: Set[StationCode], disregard: Set[StationCode], from_location: Location, dropped: bool) -> StationCode:
    for candidate in CAPTURE_SEQUENCES[Claimant(zone)]:
        if candidate in captured:
            continue
        if candidate in disregard:
            continue
        if is_capturable(zone, candidate, captured):
            return candidate
    return CAPTURE_SEQUENCES[Claimant(zone)][1]

