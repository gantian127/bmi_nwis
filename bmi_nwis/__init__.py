from .utils import NwisData
from .bmi import BmiNwis

__all__ = ["NwisData", "BmiNwis"]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
