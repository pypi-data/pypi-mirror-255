import numpy as np
import time

from .aeroshield import AeroShield


class DummyShield(AeroShield):
    def __init__(self) -> None:
        pass

    def read(self) -> tuple[float]:
        ti = time.perf_counter()

        pot = 100 + 50*np.sin(ti)
        angle = 100 + 125*np.cos(ti)

        return pot, angle

    def write(self, flag: int, motor: float):
        return int(min(max((motor), 0), 255))


    def open(self):
        return self

    def close(self, *args):
        pass

