# read version from installed package
from importlib.metadata import version
__version__ = version("python_aeroshield")

from .aeroshield import AeroShield, AeroShieldException, DummyShield
from .controller import AeroController
