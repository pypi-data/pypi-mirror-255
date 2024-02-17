from __future__ import annotations

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    import sklearn.linear_model as linear_model
    from sklearn.linear_model import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class LinearRegression(DataSpecWrapper[linear_model.LinearRegression]):
    @sarus_init("sklearn.SK_LINEAR_REGRESSION")
    def __init__(self, steps, *, memory=None, verbose=False):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


class LogisticRegression(DataSpecWrapper[linear_model.LogisticRegression]):
    @sarus_init("sklearn.SK_LOGISTIC_REGRESSION")
    def __init__(
        self,
        penalty="l2",
        dual=False,
        tol=0.0001,
        C=1.0,
        fit_intercept=True,
        intercept_scaling=1,
        class_weight=None,
        random_state=None,
        solver="lbfgs",
        max_iter=100,
        multi_class="auto",
        verbose=0,
        warm_start=False,
        n_jobs=None,
        l1_ratio=None,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


register_ops()
