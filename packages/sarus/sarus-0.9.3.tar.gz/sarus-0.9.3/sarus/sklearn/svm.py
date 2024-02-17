from __future__ import annotations

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    import sklearn.svm as svm
    from sklearn.svm import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class SVC(DataSpecWrapper[svm.SVC]):
    @sarus_init("sklearn.SK_SVC")
    def __init__(self, *args, **kwargs) -> None:
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y, sample_weight=None):
        ...


register_ops()
