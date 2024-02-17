"""Sarus Scipy package documentation."""
# flake8: noqa
try:
    import scipy.sparse as sp

    from .sparse import *
except ModuleNotFoundError:
    pass
