from __future__ import annotations

import logging
from typing import Dict, List, Optional, Union

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import sarus_init, sarus_property

try:
    import numpy.typing as npt
    import shap
    from scipy.sparse import spmatrix
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)


class Explanation(DataSpecWrapper[shap.Explanation]):
    @sarus_init("shap.SHAP_EXPLANATION")
    def __init__(
        self,
        values: Union[npt.ArrayLike, spmatrix],
        base_values: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        data: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        display_data: Optional[Dict[str, npt.ArrayLike]] = None,
        instance_names: Optional[List[str]] = None,
        feature_names: Optional[List[str]] = None,
        output_names: Optional[List[str]] = None,
        output_indexes: Optional[List[int]] = None,
        lower_bounds: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        upper_bounds: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        error_std: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        main_effects: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        hierarchical_values: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        clustering: Optional[Union[npt.ArrayLike, spmatrix]] = None,
        compute_time: Optional[float] = None,
    ):
        ...

    @sarus_property("shap.SHAP_VALUES")
    def values(self):
        ...

    @sarus_property("shap.SHAP_SUM")
    def sum(self):
        ...
