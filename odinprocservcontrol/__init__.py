from ._version_git import __version__
from .odinprocserv import OdinProcServConfig, OdinProcServControl

# __all__ defines the public API for the package.
# Each module also defines its own __all__.
__all__ = ["__version__", "OdinProcServConfig", "OdinProcServControl"]
