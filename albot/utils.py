from sr.robot import Robot

def drive(robot: Robot, common: float, differential: float = 0.0) -> None:
    robot.motors[0].m0.power = 100.0 * (common + differential)
    robot.motors[0].m1.power = 100.0 * (common - differential)
