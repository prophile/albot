from sr.robot import Robot

from albot.state import initial_state, State
from albot.view import get_world_view
from albot.decisions import choose_action
from albot.view_state_update import update_state_from_view
from albot.navmesh import get_zone

def run(robot: Robot) -> None:
    state = initial_state(robot)
    last_action = ''
    last_zone = None

    while True:
        view = get_world_view(robot)
        #print(view)
        state = update_state_from_view(state, view)
        action, state = choose_action(robot, state, view)
        action_desc = str(action)
        if action_desc != last_action:
            print("Action: ", action_desc)
            last_action = action_desc
        if state.current_zone != last_zone:
            print("Zone: ", state.current_zone, view.location)
            last_zone = state.current_zone
        state = action.perform(robot, state, view)
        robot.sleep(0.01)
