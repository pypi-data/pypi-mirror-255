"""Sarus Skopt package documentation."""
# flake8: noqa
try:
    from skopt import *
except ModuleNotFoundError:
    pass

try:
    import sarus.skopt.searchcv as searchcv
    from sarus.skopt.searchcv import BayesSearchCV
except NameError:
    pass

__all__ = ["BayesSearchCV"]
