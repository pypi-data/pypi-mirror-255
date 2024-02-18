import numpy as np

from matplotlib import pyplot as plt


class Plotter:
    def __init__(self) -> None:
        self.create_empty_figure()

    def create_empty_figure(self):
        self.fig, self.ax = plt.subplots(ncols=1, nrows=3, sharex=True)

        self.ref_line = self.ax[0].plot(0, 0, label="reference", linestyle="--", color="k")[0]
        self.angle_line = self.ax[0].plot(0, 0, label="angle")[0]
        self.ax[0].legend()
        self.ax[0].set_title("Reference tracking")
        self.ax[0].set_ylabel(r"Angle [$\degree$]")
        self.ax[0].grid(True)

        self.motor_line = self.ax[1].plot(0, 0, label="motor")[0]
        self.pot_line = self.ax[1].plot(0, 0, label="potentiometer")[0]
        self.ax[1].legend()
        self.ax[1].set_title("Input")
        self.ax[1].set_ylabel("Value [%]")
        self.ax[1].grid(True)

        self.dt_line = self.ax[2].plot(0, 0, label="dt")[0]
        self.ax[2].set_title("Time steps")
        self.ax[2].set_xlabel("Time [s]")
        self.ax[2].set_ylabel("dt [ms]")
        self.ax[2].grid(True)

    def plot(self, hist):
        self.ref_line.set_data(hist[:, 0], hist[:, 1])
        self.angle_line.set_data(hist[:, 0], hist[:, 3])
        self.ax[0].relim()
        self.ax[0].autoscale_view()

        self.motor_line.set_data(hist[:, 0], hist[:, 4]/2.55)
        self.pot_line.set_data(hist[:, 0], hist[:, 2]/10.23)
        self.ax[1].relim()
        self.ax[1].autoscale_view()

        self.dt_line.set_data(hist[:, 0], 1000*np.gradient(hist[:, 0]))
        self.ax[2].relim()
        self.ax[2].autoscale_view()

        return self.fig, self.ax
