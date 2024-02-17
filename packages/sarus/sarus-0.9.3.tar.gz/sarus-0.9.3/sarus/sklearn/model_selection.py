from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init

try:
    import sklearn.model_selection as sk_model_selection
    from sklearn.model_selection import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class TimeSeriesSplit(DataSpecWrapper[sk_model_selection.TimeSeriesSplit]):
    @sarus_init("sklearn.SK_TIME_SERIES_SPLIT")
    def __init__(
        self,
        *,
        n_splits=5,
        n_repeats=10,
        random_state=None,
        _dataspec=None,
    ):
        ...


class RepeatedStratifiedKFold(
    DataSpecWrapper[sk_model_selection.RepeatedStratifiedKFold]
):
    @sarus_init("sklearn.SK_REPEATED_STRATIFIED_KFOLD")
    def __init__(
        self,
        *,
        n_splits=5,
        n_repeats=10,
        random_state=None,
        _dataspec=None,
    ):
        ...


class KFold(DataSpecWrapper[sk_model_selection.KFold]):
    @sarus_init("sklearn.SK_KFOLD")
    def __init__(self, n_splits=5, *, shuffle=False, random_state=None):
        ...


register_ops()
