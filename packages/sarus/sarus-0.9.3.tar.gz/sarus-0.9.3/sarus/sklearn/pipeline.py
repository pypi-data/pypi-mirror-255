from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    import sklearn.pipeline as sk_pipeline
    from sklearn.pipeline import *  # noqa: F401
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class Pipeline(DataSpecWrapper[sk_pipeline.Pipeline]):
    @sarus_init("sklearn.SK_PIPELINE")
    def __init__(self, steps, *, memory=None, verbose=False):
        ...

    @sarus_method("sklearn.SK_PIPELINE_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


register_ops()
