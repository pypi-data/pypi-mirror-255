import numpy as np
import time

from typing import Optional, Iterable

from .aeroshield import AeroShield
from .plotting import LivePlotter


class AeroController:
    def __init__(self, aero_shield:AeroShield) -> None:
        self.aero_shield = aero_shield

        self.n_base_vars = 5
        # store additional variables to save when running an experiment
        self.extra_hist_vars: dict[str, int] = dict()

        # initiate controller variables
        self.variables()

    def variables(self) -> None:
        """Define variables to be used by the controller or saved during the experiment."""
        pass

    def add_tracked_variable(self, name:str, size: Optional[int]=1) -> dict[str, int]:
        """Add a variable to the list of variables whose value should be tracked during the experiment and returned afterwards.
        Variables should be instance variables of the class, otherwise they won't be accessible!

        :param name: Name of the variable, without 'self.'
        :type name: str
        :param size: Size of the variable, e.g. 3 for a three-dimensional position vector. Defaults to 1, i.e. single values.
        :type size: int, optional
        :return: A copy of the current map of tracked variables and their respective size.
        :rtype: dict[str, int]
        """
        self.extra_hist_vars[name] = size

        return self.extra_hist_vars.copy()

    def controller(self, t: float, dt: float, ref: float, pot: float, angle: float) -> float:
        """Implement the controller here. You can subclass AeroController and overwrite the controller.

        :param t: Time since start of run in seconds.
        :type t: float
        :param dt: Length of current time step in seconds.
        :type dt: float
        :param ref: reference value for the current step.
        :type ref: float
        :param pot: potentiometer value in percent.
        :type pot: float
        :param angle: calibrated angle in degrees.
        :type angle: float
        :return: input value for motor. the motor value will be saturated (int between 0 and 255 incl.) afterwards
        :rtype: float
        """

        return 0  # motor value

    def run(self, freq: int, cycles: int, ref: Optional[float | int | Iterable[float|int]]=None, live_plotter: Optional[LivePlotter]=None) -> np.ndarray:
        """Run the controller on the AeroShield.

        :param freq: Desired frequency of the loop.
        :type freq: int
        :param cycles: Number of cycles to run the experiment.
        :type duration: int
        :param ref: The reference to follow should have a lenght equal to freq * time.
        :type ref: np.ndarray[float|int]
        :param live_plotter: Optional. LivePlotter instance to use for displaying a live plot.
        :type live_plotter: LivePlotter
        """

        cntr = 0
        maxcntr = cycles
        period = 1/freq

        # calculate number of additional columns needed
        extra_hist_size = sum(self.extra_hist_vars.values())
        # t1 - tstart, ref, pot, angle, motor, any additional variables
        hist = np.zeros((maxcntr, self.n_base_vars + extra_hist_size))

        # create a zero array if no ref is given
        if ref is None:
            ref = np.zeros(maxcntr)

        # expand ref to array if given as integer/float (i.e. constant reference)
        elif isinstance(ref, (int, float)):
            ref = ref * np.ones(maxcntr)

        if live_plotter:
            live_plotter.set_up(cycles, freq)
            plot_process = live_plotter.get_process()
            plot_process.start()

        with self.aero_shield as shield:
            # need an initial write so there's something to read when we get there.
            shield.write(shield.RUN, 0)

            tstart = time.perf_counter()
            t0 = t1 = tstart

            done = False
            while not done:
                try:
                    print(f"\r{cntr}", end="")

                    while (t1 - t0) < period:
                        t1 = time.perf_counter()

                    dt = t1 - t0
                    t0 = t1

                    pot, angle = shield.read()
                    raw_motor = self.controller(t1 - tstart, dt, ref[cntr], pot, angle)
                    motor = shield.write(shield.RUN, raw_motor)

                    self._update_hist(hist, cntr, t1 - tstart, ref[cntr], pot, angle, motor)

                    if live_plotter:
                        live_plotter.add_data_to_queue(t1 - tstart, ref[cntr], angle, motor)

                    cntr += 1
                    if cntr == maxcntr:
                        done = True

                except KeyboardInterrupt:
                    done = True

            print()

        # signals to terminate live plot
        if live_plotter:
            live_plotter.add_data_to_queue(-1, -1, -1, -1)
            plot_process.join()

        return hist

    def _update_hist(self, hist: np.ndarray[float], cntr: int, t: float, ref: float, pot:float, angle: float, motor: float):
        """Update hist array with variables of the current iteration (cntr). If variables were added to `extra_hist_vars`, add them to the hist as well.

        :param hist: array to update.
        :type hist: np.ndarray[float]
        :param cntr: Iteration counter. Provides the first index to hist.
        :type cntr: int
        :param t: Time.
        :type t: float
        :param ref: Current reference value.
        :type ref: float
        :param angle: Current pendulum angle
        :type angle: float
        :param motor: Current Motor value.
        :type motor: float
        """
        hist[cntr, 0:self.n_base_vars] = t, ref, pot, angle, motor
        total_vars = self.n_base_vars

        for name, size in self.extra_hist_vars.items():
            hist[cntr, total_vars:total_vars+size] = getattr(self, name)

            total_vars += size
