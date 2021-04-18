# 1.792
# 1.760
# 1.768
# 1.800
# 1.808
# 1.824
# 1.848
# 1.808
# Mean: 1.801

# Distance covered
# Start is exactly -7
# Endpoint is -5.575
# Distance covered is 1425mm
# Compound speed is therefore 0.791m/s (at 0.8)
# Take full speed as 0.989 m/s
# Lower bound is 0.964 m/s
# Upper bound is 1.012 m/s
# Standard deviation is 0.015 m/s
# Lever arm for the wheels is 0.2
# Detection standard deviation is 80mm

import math

from albot.view import Location


MOTOR_LINEAR_SPEED = 0.989
MOTOR_LINEAR_SPEED_STDEV = 0.045
LEVER_ARM = 0.2

COMPASS_STDEV = math.radians(5)


class KalmanFilter:
    def __init__(self, initial_position: Location, initial_heading: float) -> None:
        self.location = initial_position
        self.location_error = 0.1
        self.heading = initial_heading
        self.heading_error = COMPASS_STDEV

    def tick(self, dt: float, heading: float, left_power: float, right_power: float) -> None:
        left_velocity = MOTOR_LINEAR_SPEED * left_power / 100
        right_velocity = MOTOR_LINEAR_SPEED * right_power / 100
        surge = (left_velocity + right_velocity) * 0.5
        rotation = (left_velocity - right_velocity) / LEVER_ARM
        self.location = Location(
            x=self.location.x + surge * math.sin(heading) * dt,
            y=self.location.y + surge * math.cos(heading) * dt,
        )
        self.location_error += MOTOR_LINEAR_SPEED_STDEV * dt * (0.1 + abs(surge) / MOTOR_LINEAR_SPEED)
        self.heading = (self.heading + rotation * dt) % math.tau
        self.heading_error += COMPASS_STDEV * dt

    def update_heading(self, compass: float) -> None:
        err_θ = compass - self.heading
        err_θ = (err_θ + math.pi) % math.tau - math.pi
        kalman_gain = self.heading_error / (self.heading_error + abs(err_θ) + COMPASS_STDEV)
        print(f"Heading error is {math.degrees(err_θ):.1f}°, kalman gain is {kalman_gain:.4f}")
        self.heading += kalman_gain * err_θ
        self.heading = self.heading % math.tau
        self.heading_error *= 1 - kalman_gain

    def update_location(self, location: Location, stdev: float) -> None:
        err_x = location.x - self.location.x
        err_y = location.y - self.location.y
        overall_error = math.hypot(err_x, err_y)
        kalman_gain = self.location_error / (self.location_error + overall_error + stdev)
        #print(f"Kalman gain is {kalman_gain}")
        self.location = Location(
            x=self.location.x + kalman_gain * err_x,
            y=self.location.y + kalman_gain * err_y,
        )
        self.location_error *= 1 - kalman_gain
