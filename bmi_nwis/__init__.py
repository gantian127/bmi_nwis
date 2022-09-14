from .utils import NwisData
from .bmi import BmiNwis
from ._version import get_versions

__all__ = ["NwisData", "BmiNwis"]

__version__ = get_versions()['version']
del get_versions
