from typing import Callable


class PIDController:
    def __init__(
        self,
        full_deflection_error: float,
        prediction_time: float,
        fine_tune_time: float,
        time: Callable[[], float],
    ) -> None:
        self.time = time
        self.kp = 1 / full_deflection_error
        self.kd = prediction_time / full_deflection_error
        self.ki = 1 / (fine_tune_time * full_deflection_error)
        self.t = time()
        self.last_error = 0.0
        self.accumulator = 0.0

    def step(self, error: float) -> float:
        new_time = self.time()
        dt = new_time - self.t
        self.t = new_time

        if dt > 0.2:
            dt = 0.2

        derivative = (error - self.last_error) / dt
        self.last_error = error
        self.accumulator += error * dt

        total = self.kp * error + self.kd * derivative + self.ki * self.accumulator

        if total < -1.0:
            return -1.0
        if total > 1.0:
            return 1.0
        return total

