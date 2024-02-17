"""Sarus optbinning package documentation."""
# flake8: noqa
from sarus.utils import register_ops

try:
    from optbinning import *
    from .binning import *

except ModuleNotFoundError:
    pass


register_ops()
