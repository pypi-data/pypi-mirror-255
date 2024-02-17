from __future__ import annotations

from functools import partial
from typing import Any, Optional

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    import xgboost
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing

sarus_method = partial(sarus_method, use_parent_module=True)
sarus_init = partial(sarus_init, use_parent_module=True)


class XGBClassifier(DataSpecWrapper[xgboost.XGBClassifier]):
    @sarus_init("xgboost.XGB_CLASSIFIER")
    def __init__(
        self,
        *,
        objective="binary:logistic",
        use_label_encoder: Optional[bool] = None,
        _dataspec=None,
        **kwargs: Any,
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y, sample_weight=None):
        ...


class XGBRegressor(DataSpecWrapper[xgboost.XGBRegressor]):
    @sarus_init("xgboost.XGB_REGRESSOR")
    def __init__(
        self, *, objective="reg:squarederror", _dataspec=None, **kwargs
    ):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y, sample_weight=None):
        ...


register_ops(use_parent_module=True)
