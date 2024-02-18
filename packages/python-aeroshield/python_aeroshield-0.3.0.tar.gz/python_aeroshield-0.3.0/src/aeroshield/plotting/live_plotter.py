import numpy as np

from matplotlib import pyplot as plt
from multiprocessing import Pipe, Process

from .plotter import Plotter


class LivePlotter(Plotter):
    def __init__(self) -> None:
        super().__init__()

        self.fig.canvas.mpl_connect("close_event", self.close)

        self.receiving_conn, self.sending_conn = Pipe(duplex=False)
        self.cntr = 0

        self.updating = True

        self.t_data = 0
        self.ref_data = 0
        self.angle_data = 0
        self.motor_data = 0

    def set_up(self, cycles, freq) -> None:
        max_time = cycles // freq

        self.ax[0].set_xlim(-.05, 1.01*max_time)
        # for generalisation, this range could be increased to the full range of motion of the pendulum.
        self.ax[0].set_ylim(-5, 180)

        self.ax[1].set_xlim(-.05, 1.01*max_time)
        self.ax[1].set_ylim(-5, 260)

        self.ax[2].set_xlim(-.05, 1.01*max_time)
        self.ax[2].set_ylim(1000/freq - .05, 2000/freq)

        self.t_data = np.zeros(cycles)
        self.ref_data = np.zeros(cycles)
        self.angle_data = np.zeros(cycles)
        self.motor_data = np.zeros(cycles)

    def add_data_to_queue(self, t, ref, angle, motor):
        self.sending_conn.send((t, ref, angle, motor))

    def get_data_from_queue(self):
        done = False
        while not done:
            if self.receiving_conn.poll():
                data = self.receiving_conn.recv()
                if data[0] == -1:
                    self.updating = False

                else:
                    self.t_data[self.cntr], self.ref_data[self.cntr], self.angle_data[self.cntr], self.motor_data[self.cntr] = data

                self.cntr += 1

            else:
                done = True

    def get_process(self):
        return Process(target=self.run, daemon=True)

    def run(self):
        self.updating = True

        while self.updating:
            self.get_data_from_queue()

            if self.cntr > 0:
                self.ref_line.set_data(self.t_data[:self.cntr], self.ref_data[:self.cntr])
                self.angle_line.set_data(self.t_data[:self.cntr], self.angle_data[:self.cntr])
                self.motor_line.set_data(self.t_data[:self.cntr], self.motor_data[:self.cntr])
                self.dt_line.set_data(self.t_data[:self.cntr], 1000*np.gradient(self.t_data[:self.cntr]))

            self.fig.canvas.draw()

            plt.pause(1/60)

        plt.show()

    def close(self, event):
        self.updating = False
        plt.close(self.fig)
