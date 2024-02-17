from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Union

import numpy as np
import pandas as pd

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import sarus_init, sarus_method

try:
    import shap
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)


class Masker(DataSpecWrapper[shap.maskers.Masker]):
    @sarus_init("shap.SHAP_MASKER")
    def __init__(self, **kwargs):
        ...


class Independent(DataSpecWrapper[shap.maskers.Independent]):
    @sarus_init("shap.SHAP_INDEPENDENT")
    def __init__(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        max_samples: Optional[int] = 100,
    ):
        ...

    @sarus_method("shap.SHAP_INVARIANTS")
    def invariants(self, x: Union[np.ndarray, pd.DataFrame]) -> Any:
        ...


class Partition(DataSpecWrapper[shap.maskers.Partition]):
    @sarus_init("shap.SHAP_MASKER_PARTITION")
    def __init__(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        max_samples: int = 100,
        clustering: str = "correlation",
    ):
        ...

    @sarus_method("shap.SHAP_PARTITION_INVARIANTS")
    def invariants(self, x: np.ndarray):
        ...


class Impute(DataSpecWrapper[shap.maskers.Impute]):
    @sarus_init("shap.SHAP_IMPUTE")
    def __init__(
        self,
        data: Union[np.ndarray, pd.DataFrame, Dict[str, np.ndarray]],
        method: str = "linear",
    ):
        ...


class Fixed(DataSpecWrapper[shap.maskers.Fixed]):
    @sarus_init("shap.SHAP_FIXED")
    def __init__(self):
        ...

    @sarus_method("shap.SHAP_FIXED_MASK_SHAPES")
    def invariants(
        self, X: Union[np.ndarray, pd.DataFrame, Dict[str, np.ndarray]]
    ):
        ...


class Composite(DataSpecWrapper[shap.maskers.Composite]):
    @sarus_init("shap.SHAP_COMPOSITE")
    def __init__(self, mask1: Any, mask2: Any = None, mask3: Any = None):
        ...


class FixedComposite(DataSpecWrapper[shap.maskers.FixedComposite]):
    @sarus_init("shap.SHAP_FIXED_COMPOSITE")
    def __init__(self, masker: Any):
        ...


class SHAP_OutputComposite(DataSpecWrapper[shap.maskers.OutputComposite]):
    @sarus_init("shap.SHAP_OUTPUT_COMPOSITE")
    def __init__(self, masker: shap.maskers.Masker, model: shap.models.Model):
        ...


# SHAP Text Masker
class TextMasker:
    @sarus_init("shap.SHAP_TEXT_MASKER")
    def __init__(
        self,
        tokenizer: Optional[Union[Callable, None]] = None,
        mask_token: Optional[Union[str, int, None]] = None,
        collapse_mask_token: Optional[Union[bool, str]] = "auto",
        output_type: Optional[str] = "string",
    ):
        ...

    @sarus_method("shap.SHAP_CLUSTERING")
    def clustering(self, s: str):
        ...

    @sarus_method("shap.SHAP_DATA_TEXT_TRANSFORM")
    def data_transform(self, s: str):
        ...

    @sarus_method("shap.SHAP_FEATURE_NAMES")
    def feature_names(self, s: str):
        ...

    @sarus_method("shap.SHAP_TEXT_INVARIANTS")
    def invariants(self, s: str):
        ...

    @sarus_method("shap.SHAP_MASK_TEXT_SHAPES")
    def mask_shapes(self, s: str):
        ...

    @sarus_method("shap.SHAP_SHAPE")
    def shape(self, s: str):
        ...

    @sarus_method("shap.SHAP_TOKEN_SEGMENTS")
    def token_segments(self, s: str):
        ...


# SHAP Image Masker
class ImageMasker:
    @sarus_init("shap.SHAP_IMAGE_MASKER")
    def __init__(
        self,
        mask_value: Union[np.array, str] = None,
        shape: Optional[tuple] = None,
    ):
        ...

    @sarus_method("shap.SHAP_BUILD_PARTITION_TREE")
    def build_partition_tree(self):
        ...

    @sarus_method("shap.SHAP_INPAINT")
    def inpaint(
        self,
        x: Union[pd.Series, pd.DataFrame, np.array],
        mask: Union[pd.Series, pd.DataFrame, np.array],
        method: str,
    ):
        ...
