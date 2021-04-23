import math
from sr.robot import Robot

from albot.kalman import LEVER_ARM, MOTOR_LINEAR_SPEED

def drive(robot: Robot, forward: float, turn_rate: float = 0.0) -> None:
    differential = -LEVER_ARM * turn_rate / MOTOR_LINEAR_SPEED
    # Solve common term so that forward is closest to optimal
    max_common = 1 - 2 * abs(differential)
    min_common = -1 + 2 * abs(differential)
    common = forward
    common = max(min_common, common)
    common = min(max_common, common)
    left = 100 * (common - differential)
    right = 100 * (common + differential)
    print(f"Desired: forward @ {forward:.2f}, turn rate @ {math.degrees(turn_rate):.1f}°/s; left={left:.1f}%, right={right:.1f}%; com={common:.3f} diff={differential:.3f}")
    robot.motors[0].m0.power = left
    robot.motors[0].m1.power = right
