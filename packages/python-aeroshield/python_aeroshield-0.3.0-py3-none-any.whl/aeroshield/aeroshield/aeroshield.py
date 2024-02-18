import numpy as np
import serial
import serial.tools.list_ports
import time

from typing import Optional

from .exception import AeroShieldException


class AeroShield:
    RUN = 1
    STOP = 2

    # Wait time after opening connection
    TIMEOUT = 3

    def __init__(self, baudrate:Optional[int]=115200, port:Optional[str]=None) -> None:
        if port is None:
            port = self.find_arduino()

        self.conn = serial.Serial(port, baudrate=baudrate)
        self.conn.timeout = 1

        self.zero_angle = 0

    def find_arduino(self) -> str:
        """Get the name of the port that is connected to Arduino. Raises exception if no port was found.

        :raises AeroShieldException: Raised if no Arduino was found.
        :return: COM port of the Arduino.
        :rtype: str
        """
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.manufacturer is not None and "Arduino" in p.manufacturer:
                return p.device

        raise AeroShieldException("No Arduino Found")

    @staticmethod
    def raw_angle_to_deg(raw: int) -> float:
        """Convert raw angle to degrees.

        :param raw: 12-bit value of angle sensor.
        :type raw: int
        :return: Angle value scaled to degrees.
        :rtype: float
        """
        return raw * 360 / 4096

    @staticmethod
    def raw_angle_to_rad(raw: int) -> float:
        """Convert raw angle to radians.

        :param raw: 12-bit value of angle sensor.
        :type raw: int
        :return: Angle value scaled to radians.
        :rtype: float
        """
        return raw * np.pi / 2048

    def calibrated_angle_deg(self, raw_angle: int) -> float:
        """Convert angle to degrees and calibrate with zero angle.

        :param raw_angle: Raw 12-bit angle value.
        :type raw_angle: int
        :return: Calibrated angle in degrees.
        :rtype: float
        """

        angle = self.raw_angle_to_deg(raw_angle) - self.zero_angle
        if angle < -90:
            angle += 360

        return angle

    @staticmethod
    def raw_pot_to_percent(raw:int) -> float:
        """Convert 10-bit potentiometer reading to percentage value.

        :param raw: 10-bit potentiometer value.
        :type raw: int
        :return: Potentiometer value as percentage [0, 1).
        :rtype: float
        """
        return raw * 100 / 1024

    def read(self) -> tuple[float]:
        """Read data from Arduino. Convert potentiometer and angle readings. Calibrate angle to zero reference.

        :raises AeroShieldException: Raised if no data was received. This can happen if there was no `write` command preceding a call to `read`.
        :return: Converted and calibrated potentiometer and angle readings, in that order.
        :rtype: tuple[float]
        """
        try:
            data = self.conn.read(size=3)

            pot = data[0] // 16 * 256 + data[1]
            angle = data[0] % 16 * 256 + data[2]

            return self.raw_pot_to_percent(pot), self.calibrated_angle_deg(angle)

        except IndexError:
            raise AeroShieldException("No data received from Arduino")

    @staticmethod
    def saturate(value: float, bits: int) -> int:
        """Saturate value between `0` and `2**bits - 1`.

        :param value: Raw value.
        :type value: float
        :param bits: Number of bits.
        :type bits: int
        :return: Saturated value.
        :rtype: int
        """
        return int(min(max((value), 0), 2**bits - 1))

    def write(self, flag:int, motor:float) -> int:
        """Write run/stop flag and motor value to Arduino. Saturate the motor value.

        :param flag: `AeroShield.RUN` or `AeroShield.STOP`. The former signals normal running mode, the latter tells the Arduino to stop the motor.
        :type flag: int
        :param motor: Motor value.
        :type motor: float
        :return: Saturated 8-bit motor value.
        :rtype: int
        """
        motor = self.saturate(motor, 8)
        self.conn.write(bytes([flag, motor]))
        return motor

    def calibrate(self):
        """Read out a zero reference. Pendulum should be at rest when calling this method."""
        self.write(self.RUN, 0)
        _, self.zero_angle = self.read()

    def stop(self):
        """Send stop signal to Arduino."""
        self.write(self.STOP, 0)

    def open(self):
        """Reset buffers and open connection to Arduino if it is not open already. Wait for `AeroShield.TIMEOUT` seconds to make sure connection is established."""
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        if not self.conn.is_open:
            self.conn.open()

        time.sleep(self.TIMEOUT)

        return self

    def close(self, *args):
        """Close connection to Arduino."""
        self.conn.close()

    def __enter__(self):
        self.calibrate()
        return self.open()

    def __exit__(self, *args):
        self.stop()
        self.close(*args)
