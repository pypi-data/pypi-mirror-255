import optbinning

from sarus.dataspec_wrapper import (
    DataSpecWrapper,
)
from sarus.utils import sarus_method, sarus_init, sarus_property


class OptimalBinning(DataSpecWrapper[optbinning.OptimalBinning]):
    @sarus_init("optbinning.OPTIMAL_BINNING")
    def __init__(
        self,
        name="",
        dtype="numerical",
        prebinning_method="cart",
        solver="cp",
        divergence="iv",
        max_n_prebins=20,
        min_prebin_size=0.05,
        min_n_bins=None,
        max_n_bins=None,
        min_bin_size=None,
        max_bin_size=None,
        min_bin_n_nonevent=None,
        max_bin_n_nonevent=None,
        min_bin_n_event=None,
        max_bin_n_event=None,
        monotonic_trend="auto",
        min_event_rate_diff=0,
        max_pvalue=None,
        max_pvalue_policy="consecutive",
        gamma=0,
        outlier_detector=None,
        outlier_params=None,
        class_weight=None,
        cat_cutoff=None,
        cat_unknown=None,
        user_splits=None,
        user_splits_fixed=None,
        special_codes=None,
        split_digits=None,
        mip_solver="bop",
        time_limit=100,
        verbose=False,
    ):
        ...

    @sarus_method("optbinning.OPTIMAL_BINNING_FIT", inplace=True)
    def fit(self, x, y, sample_weight=None, check_input=False):
        ...

    @sarus_method("optbinning.OPTIMAL_BINNING_FIT_TRANSFORM")
    def fit_transform(
        self,
        x,
        y,
        sample_weight=None,
        metric="woe",
        metric_special=0,
        metric_missing=0,
        show_digits=2,
        check_input=False,
    ):
        ...

    @sarus_method("optbinning.OPTIMAL_BINNING_TRANSFORM")
    def transform(
        self,
        x,
        y,
        sample_weight=None,
        metric="woe",
        metric_special=0,
        metric_missing=0,
        show_digits=2,
        check_input=False,
    ):
        ...

    @sarus_property("optbinning.OPTIMAL_BINNING_BINNING_TABLE")
    def binning_table(self):
        ...


class BinningProcess(DataSpecWrapper[optbinning.BinningProcess]):
    @sarus_init("optbinning.BINNING_PROCESS")
    def __init__(
        self,
        variable_names,
        max_n_prebins=20,
        min_prebin_size=0.05,
        min_n_bins=None,
        max_n_bins=None,
        min_bin_size=None,
        max_bin_size=None,
        max_pvalue=None,
        max_pvalue_policy="consecutive",
        selection_criteria=None,
        fixed_variables=None,
        categorical_variables=None,
        special_codes=None,
        split_digits=None,
        binning_fit_params=None,
        binning_transform_params=None,
        n_jobs=None,
        verbose=False,
    ):
        ...

    @sarus_method("optbinning.BINNING_PROCESS_FIT", inplace=True)
    def fit(self, X, y, sample_weight=None, check_input=False):
        ...

    @sarus_method("optbinning.BINNING_PROCESS_FIT_TRANSFORM")
    def fit_transform(
        self,
        X,
        y,
        sample_weight=None,
        metric=None,
        metric_special=0,
        metric_missing=0,
        show_digits=2,
        check_input=False,
    ):
        ...

    @sarus_method("optbinning.BINNING_PROCESS_TRANSFORM")
    def transform(
        self,
        X,
        metric=None,
        metric_special=0,
        metric_missing=0,
        show_digits=2,
        check_input=False,
    ):
        ...


class BinningTable(
    DataSpecWrapper[optbinning.binning.binning_statistics.BinningTable]
):
    @sarus_init("optbinning.BINNING_TABLE")
    def __init__(
        self,
        name,
        dtype,
        special_codes,
        splits,
        n_nonevent,
        n_event,
        min_x=None,
        max_x=None,
        categories=None,
        cat_others=None,
        user_splits=None,
    ):
        ...

    @sarus_method("optbinning.BINNING_TABLE_BUILD")
    def build(
        self,
        show_digits=2,
        add_totals=True,
    ):
        ...


class Scorecard(DataSpecWrapper[optbinning.Scorecard]):
    @sarus_init("optbinning.SCORECARD")
    def __init__(
        self,
        binning_process,
        estimator,
        scaling_method=None,
        scaling_method_params=None,
        intercept_based=False,
        reverse_scorecard=False,
        rounding=False,
        verbose=False,
    ):
        ...

    @sarus_method("optbinning.SCORECARD_FIT", inplace=True)
    def fit(
        self,
        X,
        y,
        sample_weight=None,
        metric_special=0,
        metric_missing=0,
        show_digits=2,
        check_input=False,
    ):
        ...

    @sarus_method("optbinning.SCORECARD_PREDICT")
    def predict(self, X):
        ...

    @sarus_method("optbinning.SCORECARD_PREDICT_PROBA")
    def predict_proba(self, X):
        ...
