# python-aeroshield

`python-aeroshield` is a Python package that implements a Python interface to [Automationshield](https://github.com/gergelytakacs/AutomationShield)'s [Aeroshield](https://github.com/gergelytakacs/AutomationShield/wiki/AeroShield). Automationshield creates cheap and accessible tools for control engineering education in the form of Arduino shields, of which the Aeroshield is one.

This project was built to allow TU Delft students learning control engineering to use Python in their assignments, since that is what they are thought in the curriculum. This package provides a flexible controller class that lets users conveniently implement a controller and run it on the Arduino hardware.

## Installation

`python-aeroshield` requires Python >= 3.10 and can be installed with the following command:

```bash
$ pip install python-aeroshield
```

## Usage

<!-- - TODO: basic basic example, live plot visuals. link to examples -->
Below is a very simple example to get started. Read more in the [documentation](https://mrtreasurer.gitlab.io/python-aeroshield).

Use the `AeroShield` class to interface directly with the Arduino.

```python
from aeroshield import AeroShield


with AeroShield() as aero_shield:
    for _ in range(100):
        aero_shield.write(flag=aero_shield.RUN, motor=50)
        out = aero_shield.read()
        print(f"Potentiomneter [%]: {out[0]}, Angle [°]: {out[1]}")
```

Use the `AeroController` class to conveniently implement a controller.

```python
from aeroshield import AeroShield, AeroController


class MyController(AeroController):
    def controller(self, t: float, dt: float, ref: float, pot: float, angle: float) -> float:
        """Set the motor value to the provided reference."""
        return ref

# create controller instance
my_controller = MyController(AeroShield())
# run the controller on the Arduino.
hist = my_controller.run(freq=200, cycles=1000, ref=45)
```

Plot the experiment data using the `plotting.Plotter` class

```python
from aeroshield.plotting import Plotter


fig, ax = Plotter.plot(hist)
fig.show()
```

Below is an example of a figure plotting the result of a PID controller with a constant reference at 45°.

![Plot of PID controller output](https://gitlab.com/mrtreasurer/python-aeroshield/-/raw/main/docs/images/pid_controller_output.png)

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`python-aeroshield` was created by Bert Van den Abbeele. It is licensed under the terms of the MIT license.

## Credits

`python-aeroshield` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
