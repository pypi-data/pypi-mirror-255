from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    from scipy.sparse import spmatrix
    from shap import Explainer, KernelExplainer, explainers
    from shap.maskers import Masker
    from shap.models import Model
    from sklearn.base import BaseEstimator
except ModuleNotFoundError:
    pass


class Explainer(DataSpecWrapper[Explainer]):
    @sarus_init("shap.SHAP_EXPLAINER")
    def __init__(
        self,
        model,
        masker: Optional[Union[Callable, np.ndarray, pd.DataFrame]] = None,
        link: Optional[Callable] = None,
        algorithm="auto",
        output_names: Optional[List[str]] = None,
        feature_names: Optional[List[str]] = None,
        linearize_link: bool = True,
        seed: Optional[int] = None,
    ):
        ...

    @sarus_method("shap.SHAP_SAVE")
    def save(
        self,
        out_file: Any,
        model_saver: str = ".save",
        masker_saver: str = ".save",
    ):
        ...

    @classmethod
    @sarus_method("shap.SHAP_LOAD")
    def load(
        cls,
        in_file: Any,
        model_loader: Callable = Model.load,
        masker_loader: Callable = Masker.load,
        instantiate: bool = True,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Tree(DataSpecWrapper[explainers.Tree]):
    @sarus_init("shap.SHAP_TREE")
    def __init__(
        self,
        model: Any,
        data: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        model_output: str = "raw",
        feature_perturbation: str = "interventional",
        feature_names: Optional[List[str]] = None,
        approximate: bool = False,
    ):
        ...

    @sarus_method("shap.SHAP_TREE_SHAP_VALUES")
    def shap_values(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[np.ndarray] = None,
        tree_limit: Optional[int] = None,
        approximate: bool = False,
        check_additivity: bool = True,
        from_call: bool = False,
    ):
        ...

    @sarus_method("shap.SHAP_TREE_SHAP_INTERACTION_VALUES")
    def shap_interaction_values(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[np.ndarray] = None,
        tree_limit: Optional[int] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class GPUTree(DataSpecWrapper[explainers.GPUTree]):
    @sarus_init("shap.SHAP_GPUTREE")
    def __init__(
        self,
        model: Any,
        data: Optional[Union[np.ndarray, pd.DataFrame]],
        model_output: str = "raw",
        feature_perturbation: str = "interventional",
        feature_names: Optional[List[str]] = None,
        approximate: bool = False,
    ):
        ...

    @sarus_method("shap.SHAP_TREE_SHAP_VALUES")
    def shap_values(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[np.ndarray] = None,
        tree_limit: Optional[int] = None,
        approximate: bool = False,
        check_additivity: bool = True,
        from_call: bool = False,
    ):
        ...

    @sarus_method("shap.SHAP_TREE_SHAP_INTERACTION_VALUES")
    def shap_interaction_values(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Optional[np.ndarray] = None,
        tree_limit: Optional[int] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Kernel(DataSpecWrapper[KernelExplainer]):
    @sarus_init("shap.SHAP_KERNEL")
    def __init__(
        self,
        model: Callable,
        data: Any,
        link: Any = None,
    ):
        ...

    @sarus_method("shap.SHAP_RUN")
    def run(self):
        ...

    @sarus_method("shap.SHAP_ALLOCATE")
    def allocate(self):
        ...

    @sarus_method("shap.SHAP_SOLVE")
    def solve(self, fraction_evaluated: Any, dim: Any):
        ...

    @sarus_method("shap.SHAP_VARYING_GROUPS")
    def varying_groups(self, X: Any):
        ...

    @sarus_method("shap.SHAP_EXPLAIN")
    def explain(self, incoming_instance: Any):
        ...

    @sarus_method("shap.SHAP_ADD_SAMPLE")
    def addsample(self, x: np.array, m: np.array, w: float):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Linear(DataSpecWrapper[explainers.Linear]):
    @sarus_init("shap.SHAP_LINEAR")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        masker: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
        link: Any = None,
        nsamples: int = 1000,
        feature_perturbation: Optional[str] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Partition(DataSpecWrapper[explainers.Partition]):
    @sarus_init("shap.SHAP_PARTITION")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        masker: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
        output_names: Any = None,
        link: Any = None,
        nsamples: int = 1000,
        feature_perturbation: Optional[str] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Permutation(DataSpecWrapper[explainers.Permutation]):
    @sarus_init("shap.SHAP_PERMUTATION")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        masker: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
        output_names: Optional[List[str]] = None,
        link: Any = None,
        linearize_link: bool = True,
        feature_names: Optional[List[str]] = None,
        nsamples: int = 1000,
        feature_perturbation: Optional[str] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_PERMUTATION_SHAP_VALUES")
    def shap_values(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        npermutations: Optional[int] = 10,
        main_effects: Optional[bool] = False,
        error_bounds: Optional[bool] = False,
        batch_evals: Optional[bool] = True,
        silent: Optional[bool] = False,
    ) -> Any:
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Sampling(DataSpecWrapper[explainers.Sampling]):
    @sarus_init("shap.SHAP_SAMPLING")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        data: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
    ):
        ...

    @sarus_method("shap.SHAP_SAMPLING_ESTIMATE")
    def sampling_estimate(
        self,
        j: int,
        f: Callable,
        x: Union[pd.Series, pd.DataFrame, np.ndarray],
        X: Union[pd.Series, pd.DataFrame, np.ndarray],
        nsamples: Optional[int] = 10,
    ) -> Any:
        ...

    @sarus_method("shap.SHAP_RUN")
    def run(self):
        ...

    @sarus_method("shap.SHAP_ALLOCATE")
    def allocate(self):
        ...

    @sarus_method("shap.SHAP_SOLVE")
    def solve(self, fraction_evaluated: Any, dim: Any):
        ...

    @sarus_method("shap.SHAP_VARYING_GROUPS")
    def varying_groups(self, X: Any):
        ...

    @sarus_method("shap.SHAP_EXPLAIN")
    def explain(self, incoming_instance: Any):
        ...

    @sarus_method("shap.SHAP_ADD_SAMPLE")
    def addsample(self, x: np.array, m: np.array, w: float):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Exact(DataSpecWrapper[explainers.Exact]):
    @sarus_init("shap.SHAP_EXACT")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        masker: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
        link: Any = None,
        linearize_link: bool = True,
        feature_names: Optional[List[str]] = None,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


class Additive(DataSpecWrapper[explainers.Additive]):
    @sarus_init("shap.SHAP_ADDITIVE")
    def __init__(
        self,
        model: Union[BaseEstimator, Tuple[Any, Any]],
        masker: Union[Tuple[Any, Any], np.ndarray, pd.DataFrame, spmatrix],
        link: Any = None,
        feature_names: Optional[List[str]] = None,
        linearize_link: Optional[bool] = True,
    ):
        ...

    @sarus_method("shap.SHAP_EXPLAIN_ROW")
    def explain_row(
        self,
        row_args: Any = None,
        max_evals: Any = None,
        main_effects: Any = None,
        error_bounds: Any = None,
        batch_size: Any = None,
        outputs: Any = None,
        silent: bool = None,
    ):
        ...

    @sarus_method("shap.SHAP_SHAP_VALUES")
    def shap_values(self, X: Union[np.ndarray, pd.DataFrame]):
        ...

    @sarus_method("shap.SHAP_CALL")
    def __call__(self, X: Union[np.ndarray, pd.DataFrame]):
        ...


register_ops()
