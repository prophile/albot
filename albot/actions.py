import abc
import math
import random
import dataclasses

from albot.state import State
from albot.view import View, Location, STATION_CODE_LOCATIONS
from albot.planning import PREDECESSORS
from albot.utils import drive
from albot.navmesh import get_zone, is_direct_routable, OPTIMAL_CAPTURE_ANGLES
from sr.robot import Robot, StationCode, Claimant


class Action(abc.ABC):
    @abc.abstractmethod
    def perform(self, robot: Robot, state: State, view: View) -> None:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class DoNothing(Action):
    def perform(self, robot: Robot, state: State, view: View) -> None:
        drive(robot, 0)


@dataclasses.dataclass(frozen=True)
class MoveRandomly(Action):
    def perform(self, robot: Robot, state: State, view: View) -> None:
        drive(robot, random.random() - 0.25, 0.25 * (random.random() - 0.5))
        robot.sleep(0.2 + random.random() * 1.3)


STEERING_THRESHOLD_METRES = 1.3
TOWER_RADIUS = 0.1
RADIANS_ERROR_AT_FULL_DEFLECTION = math.radians(60)
TOWER_ANGLE = math.radians(120)
IN_PLACE_TURN_RATE_PER_SECOND = math.radians(150)
FULL_DEFLECTION_TURN_RATE_PER_SEOND = math.radians(150)


class GoRelative(Action):
    @abc.abstractmethod
    def relative_bearing(self, state: State, view: View) -> float:
        raise NotImplementedError

    def perform(self, robot: Robot, state: State, view: View) -> None:
        heading_error = self.relative_bearing(state, view)
        heading_error = (math.pi + heading_error) % math.tau - math.pi
        print(f"  RB is {math.degrees(heading_error)}°", end='')
        # Add some pseudo heading error if the proximity sensors are going off
        left_distance = view.left_distance
        right_distance = view.right_distance

        # Detect towers
        for station in StationCode:
            station_position = STATION_CODE_LOCATIONS[station]
            distance = math.hypot(
                station_position.x - state.kalman.location.x,
                station_position.y - state.kalman.location.y,
            )
            distance = max(0, distance - TOWER_RADIUS)
            if distance > STEERING_THRESHOLD_METRES:
                continue
            absolute_bearing = math.atan2(
                station_position.x - state.kalman.location.x,
                station_position.y - state.kalman.location.y,
            ) % math.tau
            relative_bearing = absolute_bearing - state.kalman.heading
            #print(f"Proximity to {station.value}, range is {distance:.03f}m, relative {math.degrees(relative_bearing):.0f}°")
            if 0 < relative_bearing < TOWER_ANGLE:
                right_distance = min(right_distance, distance)
            elif -TOWER_ANGLE < relative_bearing <= 0:
                left_distance = min(left_distance, distance)

        turn_back = False
        if view.left_distance < STEERING_THRESHOLD_METRES:
            heading_error += RADIANS_ERROR_AT_FULL_DEFLECTION * (1 - (left_distance / STEERING_THRESHOLD_METRES))
            turn_back = True
        if view.right_distance < STEERING_THRESHOLD_METRES:
            heading_error -= RADIANS_ERROR_AT_FULL_DEFLECTION * (1 - (right_distance / STEERING_THRESHOLD_METRES))
            turn_back = True
        if turn_back:
            print(f", steering {math.degrees(heading_error)}°", end='')
        if -0.7 < heading_error < 0.7:
            print("... moving ahead")
            deflection = state.heading_pid.step(heading_error)
            drive(robot, 1, FULL_DEFLECTION_TURN_RATE_PER_SEOND * deflection)
        elif heading_error > 0:
            print("... turning right")
            drive(robot, -0.2 if turn_back else 0.2, IN_PLACE_TURN_RATE_PER_SECOND)
        elif heading_error < 0:
            print("... turning left")
            drive(robot, -0.2 if turn_back else 0.2, -IN_PLACE_TURN_RATE_PER_SECOND)
        robot.sleep(1 / 50)


class Go(GoRelative):
    @abc.abstractmethod
    def heading(self, state: State, view: View) -> float:
        raise NotImplementedError

    def relative_bearing(self, state: State, view: View) -> float:
        required_heading = self.heading(state, view)
        #print(f"Required heading is {math.degrees(required_heading) % 360}°, current is {math.degrees(view.heading) % 360}°")
        return required_heading - state.kalman.heading


@dataclasses.dataclass(frozen=True)
class GoHeading(Go):
    fixed_heading: float

    def heading(self, state: State, view: View) -> float:
        return self.fixed_heading


class Goto(Go):
    @abc.abstractmethod
    def target(self) -> Location:
        raise NotImplementedError

    def heading(self, state: State, view: View) -> float:
        target = self.target()
        #print("Target is: ", target, self)
        heading = math.atan2(target.x - state.kalman.location.x, target.y - state.kalman.location.y)
        print(f"Target {target} ({self}) direct routing on heading {math.degrees(heading) % 360:.0f}°")
        return heading


@dataclasses.dataclass
class GotoLocation(Goto):
    location: Location

    def target(self) -> Location:
        return self.location


@dataclasses.dataclass
class GotoStation(Goto):
    station: StationCode

    def target(self) -> Location:
        location = STATION_CODE_LOCATIONS[self.station]
        try:
            optimal_capture_angle = OPTIMAL_CAPTURE_ANGLES[self.station]
        except KeyError:
            return location
        else:
            return Location(
                x=location.x + math.sin(optimal_capture_angle) * 0.4,
                y=location.y + math.cos(optimal_capture_angle) * 0.4,
            )


@dataclasses.dataclass(frozen=True)
class ClaimImmediate(Action):
    station: StationCode

    def perform(self, robot: Robot, state: State, view: View) -> None:
        drive(robot, 0)
        robot.radio.claim_territory()
        new_targets = robot.radio.sweep()
        successful = False
        for target in new_targets:
            if target.target_info.station_code == self.station:
                if target.target_info.owned_by == state.zone:
                    successful = True
                break
        if successful:
            # We claimed this one, mark all downstreams as now capturable
            new_uncapturable = set(state.uncapturable)
            new_uncapturable.discard(self.station)
            for successor, predecessors in PREDECESSORS[Claimant(robot.zone)].items():
                if predecessors is None:
                    continue
                if self.station in predecessors:
                    new_uncapturable.discard(successor)
            new_cap_count = dict(state.num_captures)
            new_cap_count[self.station] += 1
            state.uncapturable = frozenset(new_uncapturable)
            state.num_captures = new_cap_count
        else:
            # We failed to claim this one, assume that all predecessors became unowned
            predecessors = PREDECESSORS[Claimant(robot.zone)][self.station]
            if predecessors is None:
                new_owned = state.captured
            else:
                new_owned = frozenset(state.captured - set(predecessors))
            state.uncapturable = state.uncapturable | {self.station}
            state.captured = new_owned
        drive(robot, -0.5)
        robot.sleep(0.2)


@dataclasses.dataclass(frozen=True)
class BackOff(Action):
    def perform(self, robot: Robot, state: State, view: View) -> State:
        drive(robot, -0.6, IN_PLACE_TURN_RATE_PER_SECOND * (0.15 * random.random() + 0.4))
        robot.sleep(0.4)
